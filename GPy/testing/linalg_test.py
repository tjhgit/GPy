import numpy as np
import scipy as sp
from ..util.linalg import jitchol

class LinalgTests(np.testing.TestCase):
    def setUp(self):
        #Create PD matrix
        A = np.random.randn(20,100)
        self.A = A.dot(A.T)
        #compute Eigdecomp
        vals, vectors = np.linalg.eig(self.A)
        #Set smallest eigenval to be negative with 5 rounds worth of jitter
        vals[vals.argmin()] = 0
        default_jitter = 1e-6*np.mean(vals)
        vals[vals.argmin()] = -default_jitter*(10**3.5)
        self.A_corrupt = (vectors * vals).dot(vectors.T)

    def test_jitchol_success(self):
        """
        Expect 5 rounds of jitter to be added and for the recovered matrix to be
        identical to the corrupted matrix apart from the jitter added to the diagonal
        """
        L = jitchol(self.A_corrupt, maxtries=5)
        A_new = L.dot(L.T)
        diff = A_new - self.A_corrupt
        np.testing.assert_allclose(diff, np.eye(A_new.shape[0])*np.diag(diff).mean(), atol=1e-13)

    def test_jitchol_failure(self):
        try:
            """
            Expecting an exception to be thrown as we expect it to require
            5 rounds of jitter to be added to enforce PDness
            """
            jitchol(self.A_corrupt, maxtries=4)
            return False
        except sp.linalg.LinAlgError:
            return True
