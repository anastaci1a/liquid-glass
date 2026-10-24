# Polarization survives changing incidence planes

The shared interface now carries a complex two-by-two energy-coherence matrix within each ray. Eighty-four interface evaluations pass energy closure, positivity and basis covariance. The twelve retained complete geometry paths also match the old two-interface primary powers within floating-point precision. No source, scene or image is accepted by these controls.

| Check | Scope |
| --- | --- |
| Normal incidence | Correct dielectric reflectance and unchanged global polarization |
| Equal indices | Zero reflection and identity transmission |
| TIR | Unit reflected flux, zero transmitted flux, retained relative phase |
| Basis gauge | Rotated input coordinates produce the same physical output matrix |
| Existing primary model | Twelve retained path pairs agree within 0.000000000000001 |

The [protocol](protocol.json), [first checkpoint](checkpoint.json), [result](result.json), [ledger](ledger.json) and [complex fixture arrays](coherence-fixtures.npz) retain exact inputs and limits. There are sixty synthetic calls and twenty-four retained-geometry interface calls. The twenty-four old Fresnel comparison points are separately counted. No new surface trace, source RGB, image or fit runs.

## Interface convention

The [implementation](../../../reconstruction/polarization_transport.py) imports the unchanged shared Snell, reflection and Fresnel-power functions. The supplied normal faces the incident medium. Two real transverse basis vectors express a Hermitian positive energy matrix. Its trace is ray power; it is not image color or calibrated radiance.

Fresnel amplitudes and TIR phase follow ordinary lossless dielectric boundary conditions; [MIT's interface notes](https://www.ocw.mit.edu/courses/6-974-fundamentals-of-photonics-quantum-electronics-spring-2006/fafcb9e36b7749f4eeb099d666bdf70a_electr_wav_inter.pdf) provide the reference derivation. Sign conventions depend on field basis and temporal phase. Here complex fields use the negative-frequency-time convention, and reflected p basis follows its actual outgoing propagation direction.

$$
c_t=\sqrt{1-\left(\frac{n_i}{n_t}\right)^2(1-c_i^2)},\qquad
r_s=\frac{n_i c_i-n_t c_t}{n_i c_i+n_t c_t},\qquad
r_p=\frac{n_t c_i-n_i c_t}{n_t c_i+n_i c_t}.
$$

The complex square root retains positive imaginary transmitted cosine under TIR. Energy-normalized transmission amplitudes use the square roots of the shared transmitted power fractions. No evanescent branch is treated as a propagating transmitted ray.

For an incidence-basis rotation and diagonal interface amplitudes, coherence transforms as

$$
\boldsymbol C_{sp}=\boldsymbol U\boldsymbol C\boldsymbol U^\dagger,\qquad
\boldsymbol C_r=\boldsymbol J_r\boldsymbol C_{sp}\boldsymbol J_r^\dagger,\qquad
\boldsymbol C_t=\boldsymbol J_t\boldsymbol C_{sp}\boldsymbol J_t^\dagger.
$$

$$
\operatorname{tr}(\boldsymbol C_r)+\operatorname{tr}(\boldsymbol C_t)
=\operatorname{tr}(\boldsymbol C).
$$

The normal-incidence fallback chooses a coordinate basis only. It changes neither a physical normal nor an optical direction. No density eigenvalue, power or score is clipped or renormalized. The original scalar interfaces and their outputs remain unchanged.

## Limits

Coherence is retained within each ray. Separate geometric paths may add intensities only under an explicitly incoherent-path model. Inter-path interference, diffraction, measured polarization, camera calibration, dispersion and Apple material identification are not established.

A blocked transmission has zero flux and unavailable direction/basis. It is not assigned a replacement ray. The next bounded transport task must preserve all emitted endpoint weights and the full encounter-cap tail, with source and environment support audited separately. Passing an interface test does not supply missing illumination or fix the visible rim.
