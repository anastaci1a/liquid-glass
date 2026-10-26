# Soft channel response

This bounded display hypothesis uses the incident-filtered, ungraded guide. It does not add white radiance or change refraction. Low-luminance neutral lift reduces the exaggerated color separation observed in pass two.

Let the guide and body be linear-light RGB vectors. The luminance weights are fixed.

$$
Y=\begin{bmatrix}0.2126&0.7152&0.0722\end{bmatrix}\boldsymbol{G},\qquad
\ell=0.12+0.38(1-Y)^2.
$$

Each channel receives a soft highlight response.

$$
E_i=1-(1-\ell)(1-G_i)^p,\qquad p\in\{1.75,2,2.25\}.
$$

A shared peak safeguard scales the endpoint without adding an independent white channel.

$$
b=\max_i B_i,\qquad
\boldsymbol{E}'=\boldsymbol{E}\max\left(1,\frac{b+0.12(1-b)}{\max_i E_i}\right).
$$

The existing integrated plateau/fade blends encoded endpoints. Pure white body remains pure white. Black reaches a neutral linear endpoint of one half. These are model choices, not measured material properties.

The body has a separate bounded low-luminance adjustment after incident sampling, before physical power and integration.

$$
\boldsymbol{C}_0=g\boldsymbol{S}+b_0,\qquad
\boldsymbol{C}=\boldsymbol{C}_0+t(1-Y_{\mathrm{S}})^3(1-\boldsymbol{C}_0),\qquad
 t\in\{0,0.08,0.16\}.
$$

Both controls are shared across expanded and compact members. Only training cohorts rank the declared settings; original held and local guards remain unchanged.
