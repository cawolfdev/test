"""VTK renderer adapter. The mesh topology/pose is fixed across camera steps."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from PIL import Image
from .domain import OrbitSpec, camera_position, shared_parallel_half_height
from .core import sha256


def load_fixed_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force='mesh', process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.vertices) == 0:
        raise ValueError('The supplied 3D asset has no triangle mesh')
    return mesh


@dataclass
class Renderer:
    """Own one immutable mesh and expose only a camera rotation operation."""
    mesh: trimesh.Trimesh
    spec: OrbitSpec

    def __post_init__(self):
        verts = self.mesh.vertices.astype('float32')
        faces = self.mesh.faces.astype(np.int64)
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(verts, deep=True))
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        # Modern VTK offsets + connectivity representation; no legacy cell API.
        offsets = np.arange(0, 3*len(faces)+1, 3, dtype=np.int64)
        cell = vtk.vtkCellArray()
        cell.SetData(numpy_to_vtk(offsets, deep=True, array_type=vtk.VTK_ID_TYPE),
                     numpy_to_vtk(faces.reshape(-1), deep=True, array_type=vtk.VTK_ID_TYPE))
        poly.SetPolys(cell)
        colors = np.ascontiguousarray(self.mesh.visual.vertex_colors[:,:3],dtype=np.uint8)
        data = numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        data.SetNumberOfComponents(3)
        poly.GetPointData().SetScalars(data)
        self._poly = poly
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        mapper.ScalarVisibilityOn()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetAmbient(.78)
        actor.GetProperty().SetDiffuse(.22)
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(.82,.85,.89)
        renderer.AddActor(actor)
        light = vtk.vtkLight()
        light.SetPosition(-4,-8,10)
        light.SetFocalPoint(0,0,1.2)
        light.SetIntensity(.7)
        renderer.AddLight(light)
        window = vtk.vtkRenderWindow()
        window.SetOffScreenRendering(True)
        window.SetSize(self.spec.width, self.spec.height)
        window.SetMultiSamples(0)
        window.AddRenderer(renderer)
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        camera.SetParallelScale(shared_parallel_half_height(self.mesh.vertices, self.spec))
        capture = vtk.vtkWindowToImageFilter()
        capture.SetInput(window)
        capture.SetInputBufferTypeToRGB()
        capture.ReadFrontBufferOff()
        self._renderer = renderer
        self._window = window
        self._camera = camera
        self._capture = capture
        self._geometry_hash = sha256_of_mesh(self.mesh)
        self._last_angle: int | None = None
        depth_capture = vtk.vtkWindowToImageFilter()
        depth_capture.SetInput(window)
        depth_capture.SetInputBufferTypeToZBuffer()
        depth_capture.ReadFrontBufferOff()
        self._depth_capture = depth_capture

    def _render_at(self, angle: int) -> None:
        if angle not in self.spec.angles:
            raise ValueError(f'{angle} not one of valid checkpoint angles {self.spec.angles}')
        if self._last_angle == angle:
            return
        pos = camera_position(angle, distance=self.spec.camera_distance, center_z=self.spec.subject_center_z)
        self._camera.SetPosition(*pos)
        self._camera.SetFocalPoint(0, 0, self.spec.subject_center_z)
        self._camera.SetViewUp(0, 0, 1)
        self._renderer.ResetCameraClippingRange()
        self._window.Render()
        self._last_angle = angle

    def render_diagnostic(self, angle: int, destination: Path, vertex_rgb: np.ndarray) -> Path:
        """Render one native-resolution visibility diagnostic without touching mesh or RGB reference.

        Per-vertex temporary colors are applied to the rendering adapter only.
        The fixed mesh object, saved checkpoint, and photographic references remain intact.
        """
        if vertex_rgb.shape != (len(self.mesh.vertices),3) or vertex_rgb.dtype != np.uint8:
            raise ValueError('Diagnostic colors must be a uint8 Nx3 array')
        original=self._poly.GetPointData().GetScalars()
        try:
            data=numpy_to_vtk(np.ascontiguousarray(vertex_rgb),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR)
            data.SetNumberOfComponents(3)
            self._poly.GetPointData().SetScalars(data)
            self._poly.Modified()
            self._last_angle=None
            return self.render(angle,destination)
        finally:
            self._poly.GetPointData().SetScalars(original)
            self._poly.Modified()
            self._last_angle=None

    def depth_buffer(self, angle: int) -> tuple[np.ndarray, float, float]:
        """Return real rasterized occlusion, with VTK's bottom-origin pixels."""
        self._render_at(angle)
        self._depth_capture.Modified()
        self._depth_capture.Update()
        data = vtk_to_numpy(self._depth_capture.GetOutput().GetPointData().GetScalars())
        z = data.reshape(self.spec.height, self.spec.width).copy()
        near, far = self._camera.GetClippingRange()
        return z, near, far

    def render(self, angle: int, destination: Path) -> Path:
        self._render_at(angle)
        self._capture.Modified()
        self._capture.Update()
        dims = self._capture.GetOutput().GetDimensions()
        rgb = vtk_to_numpy(self._capture.GetOutput().GetPointData().GetScalars()).reshape(dims[1],dims[0],3)[::-1].copy()
        destination.parent.mkdir(parents=True,exist_ok=True)
        Image.fromarray(rgb).save(destination)
        if self._geometry_hash != sha256_of_mesh(self.mesh):
            raise RuntimeError('Mesh geometry changed during camera-only orbit')
        return destination


def sha256_of_mesh(mesh: trimesh.Trimesh) -> str:
    """Geometry-only digest, independent of surface texturing."""
    import hashlib
    digest = hashlib.sha256()
    digest.update(mesh.vertices.tobytes())
    digest.update(mesh.faces.tobytes())
    return digest.hexdigest()
