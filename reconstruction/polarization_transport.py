"""Energy-normalized polarization at a lossless geometric optical interface.

Coherence is retained within a ray, including TIR phase and basis changes.
Separate geometric path intensities may be added only under an explicitly
incoherent-path model. No surface, source, fitted tone or radiance is supplied.
"""
import numpy as np
from geometric_optics import refract, reflect_direction, fresnel_components


def polarized_interface(direction, against_normal, n_from, n_to, basis, density):
    """Split a ray's 2x2 coherency into reflected/transmitted energy matrices.

    Basis rows are two real orthonormal transverse electric-field vectors.
    Complex fields use the exp(-i omega t) convention. A blocked transmission
    has zero flux matrix and NaN direction/basis, never a replacement ray.
    """
    d, n = np.asarray(direction, float), np.asarray(against_normal, float)
    B, C = np.asarray(basis, float), np.asarray(density, complex)
    shape = d.shape[:-1]
    if d.shape != n.shape or d.shape[-1:] != (3,) or B.shape != shape+(2, 3) or C.shape != shape+(2, 2):
        raise ValueError('Matched direction, basis and matrix shapes required')
    if not all(np.isfinite(v).all() for v in (d, n, B, C)):
        raise ValueError('Finite polarization data required')
    if np.max(abs(np.linalg.norm(d, axis=-1)-1)) > 1e-10 or np.max(abs(np.linalg.norm(n, axis=-1)-1)) > 1e-10:
        raise ValueError('Unit physical direction and normal required')
    if np.max(abs(B@np.swapaxes(B, -1, -2)-np.eye(2))) > 1e-10 or np.max(abs(np.sum(B*d[..., None, :], axis=-1))) > 1e-10:
        raise ValueError('Orthonormal transverse basis required')
    if np.max(abs(C-np.swapaxes(C.conj(), -1, -2))) > 1e-12 or np.min(np.linalg.eigvalsh(C)) < -1e-12:
        raise ValueError('Hermitian positive energy density required')
    ci = -np.sum(d*n, axis=-1)
    if np.any(ci <= 0):
        raise ValueError('Strict regular incidence required; tangencies are unresolved')
    ci = np.minimum(ci, 1.)
    out, blocked, discriminant = refract(d, n, n_from, n_to)
    reflected = reflect_direction(d, n)
    power = fresnel_components(ci, n_from, n_to)
    s = np.cross(d, n)
    norm = np.linalg.norm(s, axis=-1)
    # Normal incidence has no preferred incidence plane. This is a basis gauge,
    # never a change to the surface normal or either optical direction.
    s = np.divide(s, norm[..., None], out=B[..., 0, :].copy(), where=norm[..., None] > 0)
    incoming_basis = np.stack([s, np.cross(s, d)], axis=-2)
    rotation = incoming_basis@np.swapaxes(B, -1, -2)
    incoming_density = rotation@C@np.swapaxes(rotation, -1, -2)
    if n_from == n_to:
        amplitudes = np.zeros(shape+(2,), complex)
    else:
        ct = np.sqrt(discriminant.astype(complex))
        rs = (n_from*ci-n_to*ct)/(n_from*ci+n_to*ct)
        rp = (n_to*ci-n_from*ct)/(n_to*ci+n_from*ct)
        amplitudes = np.stack([rs, rp], axis=-1)
    transmitted_amplitudes = np.sqrt(1-power)
    reflected_density = amplitudes[..., :, None]*incoming_density*amplitudes.conj()[..., None, :]
    transmitted_density = transmitted_amplitudes[..., :, None]*incoming_density*transmitted_amplitudes[..., None, :]
    transmitted_density = np.where(blocked[..., None, None], 0., transmitted_density)
    reflected_basis = np.stack([s, np.cross(s, reflected)], axis=-2)
    transmitted_basis = np.stack([s, np.cross(s, out)], axis=-2)
    transmitted_basis = np.where(blocked[..., None, None], np.nan, transmitted_basis)
    input_power = np.trace(C, axis1=-2, axis2=-1).real
    reflected_power = np.trace(reflected_density, axis1=-2, axis2=-1).real
    transmitted_power = np.trace(transmitted_density, axis1=-2, axis2=-1).real
    return dict(reflected_direction=reflected, transmitted_direction=out,
                reflected_basis=reflected_basis, transmitted_basis=transmitted_basis,
                reflected_density=reflected_density, transmitted_density=transmitted_density,
                reflected_power=reflected_power, transmitted_power=transmitted_power,
                amplitudes=amplitudes, blocked=blocked, discriminant=discriminant,
                component_power=power,
                closure_error=abs(reflected_power+transmitted_power-input_power))
