# -*- coding: utf-8 -*-
import wingdbstub
import unittest
import unittest.mock

import udForDraws as ud
import k3
import sys
sys.path.append("D:\\Python33\\Lib\\site-packages")

import coverage
#----Tests
class TestUdEntity(unittest.TestCase):
    def setUp(self):
        self.ue = ud.UdEntityy()
        self.pos = self.ue.udgetpos('u99_test_UE')
        return
    
    def tearDown(self):
        self.ue=None
        return
    
class TestUdCategory(unittest.TestCase):

    def setUp(self):
        self.uc = ud.UdCategory()
        #self.ue = ud.udEn
        self.pos = self.uc.udgetpos('Drawings')
        return

    def tearDown(self):
        self.uc=None
        return
    
    def testSetUdGetpos(self):
        # Проверяем на допустимые параметры
        pos2 = self.uc.udremove("u99_testpos")
        pos = self.uc.udgetpos('Drawings')
        self.assertTrue( pos>0.,"Проверяем наличие категории Drawings в пользовательских умолчаниях. результат = "+str(pos))
        pos1 = self.uc.udaddcat(Pos=pos, Name = "testpos", Variable = "u99_testpos", Collapsed = 0,Sort = 1)
        self.assertTrue( pos1>0.,"Проверяем наличие новой категории testpos в пользовательских умолчаниях. результат = "+str(pos1))
        pos3 = self.uc.udadd
        pos2 = self.uc.udremove("u99_testpos")

        self.assertTrue( pos2==0.,"Удаляем категорию из пользовательских умолчаний")
        posFalse = self.uc.udgetpos('Drawin')
        self.assertFalse( posFalse>0.,"Проверяем наличие категории Drawin (такой нет) в пользовательских умолчаниях. результат = "+str(pos))
        
        return
        
        
def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUdCategory))
    return suite


WithCoverage=True     # С покрытием кода (отладка внутри покрытия не работает)
#WithCoverage=False    # Без покрытия кода

if __name__ == '__main__':
    suite = suite()
    if (WithCoverage==True):
        cov = coverage.coverage(config_file="d:\\PKM73_DV\\Data\\PKM\\Tests\\Python\\CoverageCfg.ini")
        cov.start()
        unittest.TextTestRunner(verbosity=2).run(suite)
    if (WithCoverage==True):
        cov.stop()
        cov.save()
        cov.html_report()
    #k3.new
    #k3.quit