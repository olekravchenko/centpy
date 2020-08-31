from .schemes1d import *

# p coefficient functions


def px_coefs(u):
    pl0 = u[j0, j0]
    pl1 = u[j0, j0] - u[jm, j0]
    pr0 = pl0.copy()
    pr1 = u[jp, j0] - u[j0, j0]

    pcx0 = pl0 - 1.0 / 12.0 * (
        u[jp, j0] + u[j0, jp] - 4.0 * u[j0, j0] + u[jm, j0] + u[j0, jm]
    )
    pcx1 = 0.5 * (pl1 + pr1)
    pcx2 = pr1 - pl1
    return pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2


def py_coefs(u):
    pb0 = u[j0, j0]
    pb1 = u[j0, j0] - u[j0, jm]
    pt0 = pb0.copy()
    pt1 = u[j0, jp] - u[j0, j0]

    pcy0 = pb0 - 1.0 / 12.0 * (
        u[jp, j0] + u[j0, jp] - 4.0 * u[j0, j0] + u[jm, j0] + u[j0, jm]
    )
    pcy1 = 0.5 * (pb1 + pt1)
    pcy2 = pt1 - pb1
    return pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2


def pdx_coefs(u):
    pl0 = u[j0, j0].copy()
    pl1 = u[j0, j0] - u[jm, jm]
    pr0 = pl0.copy()
    pr1 = u[jp, jp] - u[j0, j0]

    pcx0 = pl0 - 1.0 / 12.0 * (
        u[jp, jp] + u[jm, jp] - 4.0 * u[j0, j0] + u[jm, jm] + u[jp, jm]
    )
    pcx1 = 0.5 * (pl1 + pr1)
    pcx2 = pr1 - pl1
    return pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2


def pdy_coefs(u):
    pb0 = u[j0, j0].copy()
    pb1 = u[j0, j0] - u[jp, jm]
    pt0 = pb0.copy()
    pt1 = u[jm, jp] - u[j0, j0]

    pcy0 = pb0 - 1.0 / 12.0 * (
        u[jp, jp] + u[jm, jp] - 4.0 * u[j0, j0] + u[jm, jm] + u[jp, jm]
    )
    pcy1 = 0.5 * (pb1 + pt1)
    pcy2 = pt1 - pb1
    return pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2


#################
# Common functions minmod_prime_x, minmod_prime_y
#################

# Reuse code from schemes1d
def minmod_prime_x(u):
    return minmod_prime(u[:, 1:-1])
    # return minmod3(
    #     alpha * (u[1:-1, 1:-1] - u[:-2, 1:-1]),
    #     0.5 * (u[2:, 1:-1] - u[:-2, 1:-1]),
    #     alpha * (u[2:, 1:-1] - u[1:-1, 1:-1]),
    # )


def minmod_prime_y(u):
    return minmod3(
        alpha * (u[1:-1, 1:-1] - u[1:-1, :-2]),
        0.5 * (u[1:-1, 2:] - u[1:-1, :-2]),
        alpha * (u[1:-1, 2:] - u[1:-1, 1:-1]),
    )


# Reuse code from schemes1d
def va_prime_x(u):
    return va_prime(u[:, 1:-1])


#    return va(u[2:, 1:-1] - u[1:-1, 1:-1], u[1:-1, 1:-1] - u[:-2, 1:-1])


def va_prime_y(u):
    return va(u[1:-1, 2:] - u[1:-1, 1:-1], u[1:-1, 1:-1] - u[1:-1, :-2])


limiter_x = va_prime_x
limiter_y = va_prime_y


@dataclass
class Setup2d(Setup1d):
    # Grid parameters in the 2nd dimension
    y_init: float = 0.0
    y_final: float = 1.0
    K: int = 10


# This is the equation class including all equation-specific definitions.
class Equation2d(Equation1d):
    def __init__(self, setup):
        super().__init__(setup)
        self.y, self.dy = self.grid(self.y_init, self.y_final, self.K)
        self.xx, self.yy = np.meshgrid(self.x, self.y, sparse=True)

    @abstractmethod
    def flux_y():
        pass

    @abstractmethod
    def spectral_radius_y():
        pass


class Solver2d(Solver1d):
    def __init__(self, equation):
        super().__init__(equation)
        # Equation dependent functions
        self.flux_y = equation.flux_y
        self.spectral_radius_y = equation.spectral_radius_y

    def fd2(self, u):
        global odd
        u_star = np.ones(u.shape)
        un_half = np.ones(u.shape)
        u_prime_x = np.ones(u.shape)
        u_prime_y = np.ones(u.shape)

        u_prime_x[1:-1, 1:-1] = limiter_x(u)
        u_prime_y[1:-1, 1:-1] = limiter_y(u)

        if odd:
            un_half[1:-2, 1:-2] = 0.25 * (
                (u[1:-2, 1:-2] + u[2:-1, 1:-2] + u[1:-2, 2:-1] + u[2:-1, 2:-1])
                + 0.25
                * (
                    (u_prime_x[1:-2, 1:-2] - u_prime_x[2:-1, 1:-2])
                    + (u_prime_x[1:-2, 2:-1] - u_prime_x[2:-1, 2:-1])
                    + (u_prime_y[1:-2, 1:-2] - u_prime_y[1:-2, 2:-1])
                    + (u_prime_y[2:-1, 1:-2] - u_prime_y[2:-1, 2:-1])
                )
            )
        else:
            un_half[2:-1, 2:-1] = 0.25 * (
                (u[1:-2, 1:-2] + u[2:-1, 1:-2] + u[1:-2, 2:-1] + u[2:-1, 2:-1])
                + 0.25
                * (
                    (u_prime_x[1:-2, 1:-2] - u_prime_x[2:-1, 1:-2])
                    + (u_prime_x[1:-2, 2:-1] - u_prime_x[2:-1, 2:-1])
                    + (u_prime_y[1:-2, 1:-2] - u_prime_y[1:-2, 2:-1])
                    + (u_prime_y[2:-1, 1:-2] - u_prime_y[2:-1, 2:-1])
                )
            )

        f = self.flux_x(u)
        g = self.flux_y(u)

        f_prime_x = limiter_x(f)
        g_prime_y = limiter_y(g)

        u_star[1:-1, 1:-1] = u[1:-1, 1:-1] - 0.5 * self.dt * (
            f_prime_x / self.dx + g_prime_y / self.dy
        )
        self.boundary_conditions(u_star)
        f_star = self.flux_x(u_star)
        g_star = self.flux_y(u_star)

        if odd:
            u[1:-2, 1:-2] = (
                un_half[1:-2, 1:-2]
                - 0.5
                * self.dt
                / self.dx
                * (
                    (f_star[2:-1, 1:-2] - f_star[1:-2, 1:-2])
                    + (f_star[2:-1, 2:-1] - f_star[1:-2, 2:-1])
                )
                - 0.5
                * self.dt
                / self.dy
                * (
                    (g_star[1:-2, 2:-1] - g_star[1:-2, 1:-2])
                    + (g_star[2:-1, 2:-1] - g_star[2:-1, 1:-2])
                )
            )
        else:
            u[2:-1, 2:-1] = (
                un_half[2:-1, 2:-1]
                - 0.5
                * self.dt
                / self.dx
                * (
                    (f_star[2:-1, 1:-2] - f_star[1:-2, 1:-2])
                    + (f_star[2:-1, 2:-1] - f_star[1:-2, 2:-1])
                )
                - 0.5
                * self.dt
                / self.dy
                * (
                    (g_star[1:-2, 2:-1] - g_star[1:-2, 1:-2])
                    + (g_star[2:-1, 2:-1] - g_star[2:-1, 1:-2])
                )
            )

        self.boundary_conditions(u)
        odd = not odd
        return u

    #################
    # SD2
    #################

    def reconstruction_sd2(self, u):
        u_N, u_S, u_E, u_W = np.ones((4,) + u.shape)
        ux = limiter_x(u[1:-1, 1:-1])
        uy = limiter_y(u[1:-1, 1:-1])
        u_N[j0, j0], u_S[j0, j0], u_E[j0, j0], u_W[j0, j0] = u[None, j0, j0] + np.array(
            [0.5 * uy, -0.5 * uy, 0.5 * ux, -0.5 * ux]
        )
        list(map(self.boundary_conditions, [u_N, u_S, u_E, u_W]))
        return u_N, u_S, u_E, u_W

    def Hx_flux_sd2(self, u_E, u_W):
        a = np.maximum(self.spectral_radius_x(u_E), self.spectral_radius_x(u_W))
        f_E = self.flux_x(u_E)
        f_W = self.flux_x(u_W)
        if u_W.shape == a.shape:
            return 0.5 * (f_W + f_E) - 0.5 * a * (u_W - u_E)  # scalar
        else:
            return 0.5 * (f_W + f_E) - 0.5 * np.multiply(
                a[:, :, None], (u_W - u_E)
            )  # systems

    def Hy_flux_sd2(self, u_E, u_W):
        a = np.maximum(self.spectral_radius_y(u_E), self.spectral_radius_y(u_W))
        f_E = self.flux_y(u_E)
        f_W = self.flux_y(u_W)
        if u_W.shape == a.shape:
            return 0.5 * (f_W + f_E) - 0.5 * a * (u_W - u_E)  # scalar
        else:
            return 0.5 * (f_W + f_E) - 0.5 * np.multiply(
                a[:, :, None], (u_W - u_E)
            )  # systems

    def c_flux_sd2(self, u_N, u_S, u_E, u_W):
        Hx_halfm = self.Hx_flux_sd2(u_E[jm, j0], u_W[j0, j0])
        Hx_halfp = self.Hx_flux_sd2(u_E[j0, j0], u_W[jp, j0])
        Hy_halfm = self.Hy_flux_sd2(u_N[j0, jm], u_S[j0, j0])
        Hy_halfp = self.Hy_flux_sd2(u_N[j0, j0], u_S[j0, jp])
        return -self.dt / self.dx * (Hx_halfp - Hx_halfm) - self.dt / self.dy * (
            Hy_halfp - Hy_halfm
        )

    def sd2(self, u):
        self.boundary_conditions(u)
        u_N, u_S, u_E, u_W = self.reconstruction_sd2(u)
        C0 = self.c_flux_sd2(u_N, u_S, u_E, u_W)
        u[j0, j0] += C0
        self.boundary_conditions(u)
        u_N, u_S, u_E, u_W = self.reconstruction_sd2(u)
        C1 = self.c_flux_sd2(u_N, u_S, u_E, u_W)
        u[j0, j0] += 0.5 * (C1 - C0)
        self.boundary_conditions(u)
        return u

    #################
    # SD3
    #################

    # indicators: indicators_2d_sd3, indicators_diag_2d_sd3

    def indicators_sd3(self, u):
        u_norm = np.sqrt(self.dx * self.dy) * np.linalg.norm(u[j0, j0])

        pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2 = px_coefs(u)

        ISl = pl1 ** 2 / (u_norm + eps)
        IScx = 1.0 / (u_norm + eps) * ((13.0 / 3.0) * pcx2 ** 2 + pcx1 ** 2)
        ISr = pr1 ** 2 / (u_norm + eps)

        pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2 = py_coefs(u)

        ISb = pb1 ** 2 / (u_norm + eps)
        IScy = 1.0 / (u_norm + eps) * ((13.0 / 3.0) * pcy2 ** 2 + pcy1 ** 2)
        ISt = pt1 ** 2 / (u_norm + eps)
        return ISl, IScx, ISr, ISb, IScy, ISt

    def indicators_diag_sd3(self, u):
        u_norm = np.sqrt(self.dx * self.dy) * np.linalg.norm(u[j0, j0])

        pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2 = pdx_coefs(u)

        dISl = pl1 ** 2 / (u_norm + eps)
        dIScx = 1.0 / (u_norm + eps) * ((13.0 / 3.0) * pcx2 ** 2 + pcx1 ** 2)
        dISr = pr1 ** 2 / (u_norm + eps)

        pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2 = pdy_coefs(u)

        dISb = pb1 ** 2 / (u_norm + eps)
        dIScy = 1.0 / (u_norm + eps) * ((13.0 / 3.0) * pcy2 ** 2 + pcy1 ** 2)
        dISt = pt1 ** 2 / (u_norm + eps)
        return dISl, dIScx, dISr, dISb, dIScy, dISt

    # reconstruction: reconstruction_2d_sd3, reconstruction_diag_2d_sd3

    def reconstruction_sd3(self, u, ISl, IScx, ISr, ISb, IScy, ISt):

        u_N, u_S, u_E, u_W = np.ones((4,) + u.shape)

        cl = 0.25
        ccx = 0.5
        cr = 0.25
        cb = 0.25
        ccy = 0.5
        ct = 0.25

        pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2 = px_coefs(u)

        alpl = cl / ((eps + ISl) ** 2)
        alpcx = ccx / ((eps + IScx) ** 2)
        alpr = cr / ((eps + ISr) ** 2)
        alp_sum = alpl + alpcx + alpr
        wl = alpl / alp_sum
        wcx = alpcx / alp_sum
        wr = alpr / alp_sum

        pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2 = py_coefs(u)

        alpb = cb / ((eps + ISb) ** 2)
        alpcy = ccy / ((eps + IScy) ** 2)
        alpt = ct / ((eps + ISt) ** 2)
        alp_sum = alpb + alpcy + alpt
        wb = alpb / alp_sum
        wcy = alpcy / alp_sum
        wt = alpt / alp_sum

        u_N[j0, j0] = (
            wb * (pb0 + 0.5 * pb1)
            + wcy * (pcy0 + 0.5 * pcy1 + 0.25 * pcy2)
            + wt * (pt0 + 0.5 * pt1)
        )
        u_S[j0, j0] = (
            wb * (pb0 - 0.5 * pb1)
            + wcy * (pcy0 - 0.5 * pcy1 + 0.25 * pcy2)
            + wt * (pt0 - 0.5 * pt1)
        )
        u_E[j0, j0] = (
            wl * (pl0 + 0.5 * pl1)
            + wcx * (pcx0 + 0.5 * pcx1 + 0.25 * pcx2)
            + wr * (pr0 + 0.5 * pr1)
        )
        u_W[j0, j0] = (
            wl * (pl0 - 0.5 * pl1)
            + wcx * (pcx0 - 0.5 * pcx1 + 0.25 * pcx2)
            + wr * (pr0 - 0.5 * pr1)
        )

        return u_N, u_S, u_E, u_W

    def reconstruction_diag_sd3(self, u, dISl, dIScx, dISr, dISb, dIScy, dISt):
        u_NE, u_SE, u_NW, u_SW = np.ones((4,) + u.shape)

        cl = 0.25
        ccx = 0.5
        cr = 0.25
        cb = 0.25
        ccy = 0.5
        ct = 0.25

        pl0, pl1, pr0, pr1, pcx0, pcx1, pcx2 = pdx_coefs(u)

        alpl = cl / (eps + dISl) ** 2
        alpcx = ccx / (eps + dIScx) ** 2
        alpr = cr / (eps + dISr) ** 2
        alp_sum = alpl + alpcx + alpr
        wl = alpl / alp_sum
        wcx = alpcx / alp_sum
        wr = alpr / alp_sum

        pb0, pb1, pt0, pt1, pcy0, pcy1, pcy2 = pdy_coefs(u)

        alpb = cb / (eps + dISb) ** 2
        alpcy = ccy / (eps + dIScy) ** 2
        alpt = ct / (eps + dISt) ** 2
        alp_sum = alpb + alpcy + alpt
        wb = alpb / alp_sum
        wcy = alpcy / alp_sum
        wt = alpt / alp_sum

        u_NW[j0, j0] = (
            wb * (pb0 + 0.5 * pb1)
            + wcy * (pcy0 + 0.5 * pcy1 + 0.25 * pcy2)
            + wt * (pt0 + 0.5 * pt1)
        )
        u_SE[j0, j0] = (
            wb * (pb0 - 0.5 * pb1)
            + wcy * (pcy0 - 0.5 * pcy1 + 0.25 * pcy2)
            + wt * (pt0 - 0.5 * pt1)
        )
        u_NE[j0, j0] = (
            wl * (pl0 + 0.5 * pl1)
            + wcx * (pcx0 + 0.5 * pcx1 + 0.25 * pcx2)
            + wr * (pr0 + 0.5 * pr1)
        )
        u_SW[j0, j0] = (
            wl * (pl0 - 0.5 * pl1)
            + wcx * (pcx0 - 0.5 * pcx1 + 0.25 * pcx2)
            + wr * (pr0 - 0.5 * pr1)
        )

        return u_NW, u_SE, u_NE, u_SW

    # numerical fluxes: Hx_flux_2d_sd3, Hy_flux_2d_sd3, c_flux_2d_sd3

    def Hx_flux_sd3(self, u_NW, u_W, u_SW, u_NE, u_E, u_SE):
        a = np.maximum(self.spectral_radius_x(u_E), self.spectral_radius_x(u_W))
        f_E = self.flux_x(u_E)
        f_W = self.flux_x(u_W)
        f_NE = self.flux_x(u_NE)
        f_NW = self.flux_x(u_NW)
        f_SE = self.flux_x(u_SE)
        f_SW = self.flux_x(u_SW)

        Hx = (
            1.0
            / 12.0
            * (
                (f_NW + f_NE + 4.0 * (f_W + f_E) + f_SW + f_SE)
                - a * (u_NW - u_NE + 4.0 * (u_W - u_E) + u_SW - u_SE)
            )
        )
        return Hx

    def Hy_flux_sd3(self, u_SW, u_S, u_SE, u_NE, u_N, u_NW):
        b = np.maximum(self.spectral_radius_y(u_N), self.spectral_radius_y(u_S))
        g_N = self.flux_y(u_N)
        g_S = self.flux_y(u_S)
        g_NE = self.flux_y(u_NE)
        g_NW = self.flux_y(u_NW)
        g_SE = self.flux_y(u_SE)
        g_SW = self.flux_y(u_SW)

        Hy = (
            1.0
            / 12.0
            * (
                (g_SW + g_NW + 4.0 * (g_S + g_N) + g_SE + g_NE)
                - b * (u_SW - u_NW + 4.0 * (u_S - u_N) + u_SE - u_NE)
            )
        )
        return Hy

    def c_flux_sd3(self, u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW):
        Hx_fluxm = self.Hx_flux_sd3(
            u_NW[j0, j0],
            u_W[j0, j0],
            u_SW[j0, j0],
            u_NE[jm, j0],
            u_E[jm, j0],
            u_SE[jm, j0],
        )
        Hx_fluxp = self.Hx_flux_sd3(
            u_NW[jp, j0],
            u_W[jp, j0],
            u_SW[jp, j0],
            u_NE[j0, j0],
            u_E[j0, j0],
            u_SE[j0, j0],
        )
        Hy_fluxm = self.Hy_flux_sd3(
            u_SW[j0, j0],
            u_S[j0, j0],
            u_SE[j0, j0],
            u_NE[j0, jm],
            u_N[j0, jm],
            u_NW[j0, jm],
        )
        Hy_fluxp = self.Hy_flux_sd3(
            u_SW[j0, jp],
            u_S[j0, jp],
            u_SE[j0, jp],
            u_NE[j0, j0],
            u_N[j0, j0],
            u_NW[j0, j0],
        )
        return -self.dt / self.dx * (Hx_fluxp - Hx_fluxm) - self.dt / self.dy * (
            Hy_fluxp - Hy_fluxm
        )

    # final scheme sd3_2d

    def sd3(self, u):
        self.boundary_conditions(u)
        ISl, IScx, ISr, ISb, IScy, ISt = self.indicators_sd3(u)
        u_N, u_S, u_E, u_W = self.reconstruction_sd3(u, ISl, IScx, ISr, ISb, IScy, ISt)
        dISl, dIScx, dISr, dISb, dIScy, dISt = self.indicators_diag_sd3(u)
        u_NW, u_SE, u_NE, u_SW = self.reconstruction_diag_sd3(
            u, dISl, dIScx, dISr, dISb, dIScy, dISt
        )
        list(
            map(self.boundary_conditions, [u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW])
        )
        C0 = self.c_flux_sd3(u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW)
        u[j0, j0] += C0
        self.boundary_conditions(u)
        u_N, u_S, u_E, u_W = self.reconstruction_sd3(u, ISl, IScx, ISr, ISb, IScy, ISt)
        u_NW, u_SE, u_NE, u_SW = self.reconstruction_diag_sd3(
            u, dISl, dIScx, dISr, dISb, dIScy, dISt
        )
        list(
            map(self.boundary_conditions, [u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW])
        )
        C1 = self.c_flux_sd3(u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW)
        u[j0, j0] += 0.25 * (C1 - 3.0 * C0)
        self.boundary_conditions(u)
        u_N, u_S, u_E, u_W = self.reconstruction_sd3(u, ISl, IScx, ISr, ISb, IScy, ISt)
        u_NW, u_SE, u_NE, u_SW = self.reconstruction_diag_sd3(
            u, dISl, dIScx, dISr, dISb, dIScy, dISt
        )
        list(
            map(self.boundary_conditions, [u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW])
        )
        C2 = self.c_flux_sd3(u_N, u_S, u_E, u_W, u_NE, u_SE, u_SW, u_NW)
        u[j0, j0] += +1.0 / 12.0 * (8.0 * C2 - C1 - C0)
        self.boundary_conditions(u)
        return u

    # Main solver routine
    def solve(self):
        if self.scheme == "sd2":
            self.step = self.sd2
        elif self.scheme == "sd3":
            self.step = self.sd3
        elif self.scheme == "fd2":
            self.step = self.fd2
        else:
            sys.exit(
                "Scheme "
                + self.scheme
                + " is not recognized! Choices are: fd2, sd2, sd3."
            )
        i = 0
        t = 0.0
        t_out = 0.0
        while t < self.t_final:
            r_max_x = np.max(self.spectral_radius_x(self.u))
            r_max_y = np.max(self.spectral_radius_y(self.u))
            dt = self.cfl / np.sqrt((r_max_x / self.dx) ** 2 + (r_max_y / self.dy) ** 2)
            self.dt = min(dt, self.dt_out - t_out)
            t += self.dt
            t_out += self.dt
            self.u = self.step(self.u)
            # Store if t_out=dt_out
            if t_out == self.dt_out:
                i += 1
                self.u_n[i, :] = self.u
                t_out = 0
