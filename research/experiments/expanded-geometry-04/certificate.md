# Curved-front solid certificate

Status: a third bounded geometric hypothesis. No source, material, silhouette or scoring change is included.

## One occupied solid

The frozen convex rounded footprint bounds the solid between the original concave back and a concave parabolic front:

$$
f(\mathbf{x})=d_f\left(1-\frac{x^2}{a^2}\right),\qquad
\Omega=\{(\mathbf{x},z):\rho(\mathbf{x})\leq1,\ -h(\mathbf{x})\leq z\leq f(\mathbf{x})\}.
$$

Convex footprint, concave front and concave back imply convex occupancy. This certificate concerns occupancy; it does not assert the clipped level expression is globally convex outside the footprint.

The adapter evaluates a single level set:

$$
F(\mathbf{x},z)=\max\{z-f(\mathbf{x}),\ -z-h(\mathbf{x}),\ \rho(\mathbf{x})^2-1\}.
$$

Its active constraint supplies the outward normal. Tied constraints are creases, not independently smoothed normals. The same front and back generate sections and ordered intersections.

## Bounds and paths

The enclosing box is fixed analytically:

$$
\mathbf{c}=\begin{bmatrix}0\\0\\\frac{d_f-H}{2}\end{bmatrix},\qquad
\mathbf{e}=\begin{bmatrix}a\\b\\\frac{d_f+H}{2}\end{bmatrix},\qquad H=\max h.
$$

The original reference plane remains zero. Positive front height extends toward the viewer; the frozen background stays behind that reference plane.

Use the unchanged shared convex-solid tracer with a declared bisection tolerance. Verify entry, ordered exit, actual normals, Snell branches, background clearance and no reentry through convex occupancy.

Projected tangencies, zero-thickness poles, uncertain creases, total internal reflection and non-downward exits remain incomplete with NaN source coordinates. They are never replaced by copied pixels.

This is primary transmitted transport, not a complete radiance or reflected-environment model. A correct solid does not establish visible fidelity, identified thickness or measured Apple material.
