# Toolbar finite-gap surface diagnostic protocol

Queue17 preparation. Geometry evidence only; unchanged accepted revision2 map,
source, material, silhouette, masks and epoch. No target-image fitting or pass.

Orthographic camera propagates along negative z. Air index1, flat front z=0,
glass index n>1, unknown smooth back z=-h(x,y), background z=-G. Normal entry
leaves the internal incident ray vertical. All lengths normalize by L=170px.
Let v=F(x,y)-(x,y), s=G-h>0, R=sqrt(|v|²+s²), D=nR-s. Snell normal alignment gives

    p=grad(h)=v/D,  N=(-p_x,-p_y,-1)/sqrt(1+|p|²).

h is one surface. s cannot be chosen independently per pixel. The inverse
relation also has an inadmissible exit branch: the requested outgoing ray
(v,-s)/R must have positive dot product with N. Equivalently s>p·v, or
s>|v|/sqrt(n²-1). Equality is the critical/grazing branch, excluded here.

For C² fields define c=partial_x(v_y)-partial_y(v_x) and
K=v_y*(v·partial_x(v))-v_x*(v·partial_y(v)). Differentiating grad(h)=v/D and using
grad(s)=-p cancels the derivatives of s because p is parallel to v. A necessary
local condition for a surface is

    D*c - (n/R)*K = 0.

Dividing by D² gives the compatibility residual in gradient-curl units. This
condition still depends on unknown h through s. Nonzero c by itself does not
reject finite-gap refraction. A chosen field s that makes this condition small
is insufficient: the surface PDE, path independence, height/clearance and Snell
branch must also hold. At v=0 the formula stays regular for s>0 and n>1.

Forward verification uses a=1/sqrt(1+|p|²), Q=1-n²*(1-a²),
V=n*(0,0,-1)+(sqrt(Q)-n*a)*N, and F_h=x+(G-h)*V_xy/(-V_z).
Reject Q<=0, nonpositive outgoing descent, h<=0 or G-h<=0. Never clip a TIR ray.
A coarse grid cannot certify global clearance, side-wall avoidance or a solid.

The bounded diagnostic uses n in{1.33,1.5,1.8}, center back thickness h0=.5L,
and center clearance g in{.5,2,8}L, so G=h0+g. No parameter is selected by target
pixels. Thickness/plane translations with fixed g leave this inverse geometry
unchanged, apart from positivity constraints; no absolute thickness recovery is
claimed. Domain is the frozen crowned footprint. Only center height is imposed;
no arbitrary zero-height or constant-height boundary is forced on its edge.

Two piecewise axis paths integrate the nonlinear surface PDE from the same
center anchor: x-then-y and y-then-x. Intermediate points stay inside this
coordinate-convex footprint. Compare heights, gradient/PDE and compatibility
residuals, transmitted-branch validity, and forward-map errors. Preserve invalid
configurations. Use grid spacings .08L/.04L and RK4 steps<=.02L; repeat a
representative configuration at<=.01L only to separate integration error from
path inconsistency. Native source/filter/shading are not involved. Identity and
a known smooth transmitting quadratic surface supply independent checks.

Reference verified: [Bösel and Gross, arXiv1510.01129v2](https://arxiv.org/html/1510.01129),
sectionII.2, equations4–11. It couples the unknown surface and ray map through
Snell normal alignment and normal-field integrability; its small-angle OMT
construction is approximate. The equations above are independently derived in
the propagation and graph conventions stated here. Lead's private switch
back-surface model supplied an independent convention check, not a toolbar fit.

## Adaptive numerical review after the first bounded diagnostic

The representative n1.5,g2 path mismatch is .02706976L versus .02706949L
after halving RK steps, while forward-map errors depend appreciably on spatial
stencils. Add ONE representative .02L spatial grid at .01L RK steps. Preserve
the original grids. No target pixels or parameter optimization enter this check.

A stronger independently derived necessary condition follows from the valid
exit branch. Let M=|v|² and rho=K/c where c!=0. Compatibility requires

    rho = D*R/n = M+s²-s*sqrt(M+s²)/n.

On the transmitted branch s>sqrt(M/(n²-1)), this function is strictly increasing
from M. Therefore rho>M is necessary; wrong signs are not repaired by an
independent arbitrary gap. For rho>M, the only transmitted-branch solution is

    A=rho-M,
    s_req²=(2*n²*A+M+sqrt(M²+4*n²*A*rho))/(2*(n²-1)).

This does NOT create a source surface by assigning each pixel a gap. It only
extracts a necessary clearance field. Any actual h=G-s_req must ALSO satisfy
-grad(s_req)=v/D and height/branch/boundary conditions. At c=0 the unsimplified
condition remains required; do not divide by numerical zero. Use direct central
map derivatives at1e-4L and5e-5L, report threshold/noise sensitivity and retain
the near-zero-c set as unresolved. Validate the inversion on a known smooth
transmitting surface before interpreting the toolbar. This tests exact
representability of this specified camera/interface family; approximate map
error still requires a projection and no all-surface impossibility is implied.
