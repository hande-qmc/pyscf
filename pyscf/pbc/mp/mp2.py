from pyscf import lib
from pyscf.mp import mp2
from pyscf.mp import ump2
from pyscf.mp import gmp2

class RMP2(mp2.RMP2):
    def ao2mo(self, mo_coeff=None):
        ao2mofn = _gen_ao2mofn(self._scf)
        return mp2._make_eris(self, mo_coeff, ao2mofn, self.verbose)

class UMP2(ump2.UMP2):
    def ao2mo(self, mo_coeff=None):
        ao2mofn = _gen_ao2mofn(self._scf)
        return ump2._make_eris(self, mo_coeff, ao2mofn, self.verbose)

class GMP2(gmp2.GMP2):
    def ao2mo(self, mo_coeff=None):
        with_df = self._scf.with_df
        kpt = self._scf.kpt
        def ao2mofn(mos):
            orbo, orbv, orbo, orbv = mos
            nocc = orbo.shape[1]
            nvir = orbv.shape[1]
            nao = orbo.shape[0]
            orboa = orbo[:nao//2]
            orbob = orbo[nao//2:]
            orbva = orbv[:nao//2]
            orbvb = orbv[nao//2:]
            orbspin = getattr(orbo, 'orbspin', None)
            if orbspin is None:
                eri  = with_df.ao2mo((orboa,orbva,orboa,orbva), kpt)
                eri += with_df.ao2mo((orbob,orbvb,orbob,orbvb), kpt)
                eri1 = with_df.ao2mo((orboa,orbva,orbob,orbvb), kpt)
                eri += eri1
                eri += eri1.transpose(2,3,0,1)
                eri = eri.reshape(nocc,nvir,nocc,nvir)
            else:
                co = orboa + orbob
                cv = orbva + orbvb
                eri = with_df.ao2mo((co,cv,co,cv), kpt).reshape(nocc,nvir,nocc,nvir)
                sym_forbid = (orbspin[:nocc,None] != orbspin[nocc:])
                eri[sym_forbid,:,:] = 0
                eri[:,:,sym_forbid] = 0
            return eri
        return gmp2._make_eris_incore(self, mo_coeff, ao2mofn, self.verbose)

def _gen_ao2mofn(mf):
    with_df = mf.with_df
    kpt = mf.kpt
    def ao2mofn(mo_coeff):
        return with_df.ao2mo(mo_coeff, kpt, compact=False)
    return ao2mofn
