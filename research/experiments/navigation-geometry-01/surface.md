# Rounded-rectangle harmonic surface

This adapter reuses the expanded-control construction with the navigation control’s frozen footprint. The shared tracer supplies refraction and path classification; the adapter supplies only actual height and derivatives.

## Solid

Let the half-extents be positive, with corner radius no greater than either half-extent. The normalized distance to the inner rectangle is:

$$
\rho(x,y)=\frac{\sqrt{[|x|-(a-r)]_+^2+[|y|-(b-r)]_+^2}}{r},
\qquad [u]_+=\max(u,0).
$$

Inside the footprint, define two concave heights and their harmonic composition:

$$
h_1=d(1-\rho^p),\qquad h_2=c\left(1-\frac{x^2}{a^2}\right),
\qquad h=\frac{h_1h_2}{h_1+h_2}.
$$

The common-zero value is zero. The solid and interface normal are:

$$
\Omega=\{(x,y,z):\rho\leq1,\;-h(x,y)\leq z\leq0\},
\qquad \mathbf{n}_{\mathrm{back}}=
\frac{(-\partial_x h,-\partial_y h,-1)}{\sqrt{1+\|\nabla h\|^2}}.
$$

## Certificate and limits

Distance to the inner rectangle is convex. The two heights are concave on the footprint; positive harmonic composition is concave and nondecreasing in both inputs. The solid is therefore convex.

Global bounds used by the shared primary tracer are:

$$
h\leq\frac{dc}{d+c},\qquad
\|\nabla h\|\leq\max\left(\frac{pd}{r},\frac{2c}{a}\right).
$$

The surface is C1, with second-derivative jumps at joins. Front/back rim creases and exact zero-height poles are unresolved paths, not transmitted samples. The current core enforces this explicitly.

The isotropic fixture replaces the longitudinal quadratic with a radial quadratic. It agrees with the shared circular harmonic surface; this fixture does not claim an elongated surface is rotationally symmetric.

[Numerical controls](geometry-check.json) check analytical gradients, circle equality, bounds and pole classification. They do not establish visible fidelity or recovered physical dimensions.
