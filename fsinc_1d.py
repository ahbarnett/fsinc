import numpy as np
import finufftpy as nufft
import fastgl

def sinc1d(x, s, xp, norm = False):
  """
  Calculate the fast sinc-transform by ways of the non-uniform fast Fourier transform.

  sp = sum sinc(x - xp) * s

  Args:
    x (array, floats): sample points
    s (array, floats or complex): sample values at x
    xp (array, floats): target grid
    norm (bool): use normalized sinc: sinc(pi*x)/pi*x (default: False)

  Returns:
    sp (array, floats): transformed signal to xp
  """

  eps = 1.e-15

  # normalized sinc
  if norm:
    x = x * np.pi
    xp = xp * np.pi

  xm = np.max( [np.max(np.abs(x)), np.max(np.abs(xp)) ])

  resample = 2 # resample rate
  nx = np.ceil(resample * np.round(xm + 3)).astype('int')

  print('calculate Legendre-Gauss weights (using fastgl)', nx)
  xx, ww = fastgl.lgwt(nx)

  print('nufft1')
  h = np.zeros(xx.shape, dtype = np.complex128) # signal at xx (G-L nodes)
  status = nufft.nufft1d3(x, s, -1, eps, xx, h, debug = 1, spread_debug = 1)
  assert status == 0

  # integrate signal using G-L quadrature
  ws = h * ww

  print('nufft2')
  sp = np.zeros(xp.shape, dtype = np.complex128) # signal at xx
  status = nufft.nufft1d3(xx, ws, 1, eps, xp, sp, debug = 1, spread_debug = 1)
  sp = .5 * sp
  assert status == 0

  if np.all(np.isreal(s)):
    return sp.real
  else:
    return sp


def sincsq1d(x, s, xp, norm = False):
  """
  Calculate the fast sinc^2-transform by ways of the non-uniform fast Fourier transform.

  sp = sum sinc^2(x - xp) * s

  Args:
    x (array, floats): sample points
    s (array, floats or complex): sample values at x
    xp (array, floats): target grid
    norm (bool): use normalized sinc: sinc(pi*x)/pi*x (default: False)

  Returns:
    sp (array, floats): transformed signal to xp
  """
  assert len(x) == len(s)

  eps = 1.e-15

  # normalized sinc
  if norm:
    x = x * np.pi
    xp = xp * np.pi

  xm = np.max( [np.max(np.abs(x)), np.max(np.abs(xp)) ])

  resample = 2 # resample rate
  nx = np.ceil(resample * np.round(xm + 3)).astype('int')

  # calculate Legendre-Gauss quadrature weights
  print('calculate Legendre-Gauss weights (using fastgl)', nx)
  xx, ww = fastgl.lgwt(nx)
  xx = np.concatenate((xx-1, xx+1)) # covers [-2, 2]
  ww = np.concatenate((ww, ww))

  print('nufft1')
  h = np.zeros(xx.shape, dtype = np.complex128) # signal at xx
  status = nufft.nufft1d3(x, s, -1, eps, xx, h, debug = 1, spread_debug = 1)
  assert status == 0

  # integrated signal
  ws = h * ww * (2 - np.abs(xx))

  print('nufft2')
  sp = np.zeros(xp.shape, dtype = np.complex128) # signal at xx
  status = nufft.nufft1d3(xx, ws, 1, eps, xp, sp, debug = 1, spread_debug = 1)
  sp = sp * 0.25
  assert status == 0

  if np.all(np.isreal(s)):
    return sp.real
  else:
    return sp

