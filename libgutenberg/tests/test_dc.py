#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest

from libgutenberg.CommonOptions import Options
from libgutenberg import GutenbergDatabase, GutenbergDatabaseDublinCore, DummyConnectionPool
from libgutenberg import DublinCoreMapping

db_exists = GutenbergDatabase.db_exists

options = Options()
options.config = None

@unittest.skipIf(not db_exists, 'database not configured')
class TestDC(unittest.TestCase):
    ebook = 20050
    title = "Märchen der Gebrüder Grimm 1"
    ebook2 = 2600 # war and peace

    def setUp(self):
        GutenbergDatabase.DB = GutenbergDatabase.Database()
        GutenbergDatabase.DB.connect()
        self.dummypool = DummyConnectionPool.ConnectionPool()
        #self.dc2 = self.dc
        

    def test_metadata(self):
        dc = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        self.metadata_test1(dc)
        dc = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        self.metadata_test2(dc)

    def test_orm_metadata(self):
        dc = DublinCoreMapping.DublinCoreObject()
        self.metadata_test1(dc)
        dc = DublinCoreMapping.DublinCoreObject()
        self.metadata_test2(dc)

    def metadata_test1(self, dc):
        dc.load_from_database(self.ebook)
        self.assertEqual(dc.project_gutenberg_id, 20050)
        self.assertEqual(dc.title, self.title)
        self.assertEqual(dc.rights, 'Public domain in the USA.')
        self.assertEqual(str(dc.release_date), '2006-12-09')
        self.assertEqual(dc.languages[0].id, 'de')
        self.assertEqual(dc.marcs[0].code, '245')
        self.assertEqual(dc.marcs[0].caption, 'Title')
        self.assertEqual(dc.title, dc.title_file_as)
        self.assertEqual(len(dc.authors), 2)
        author = dc.authors[0]
        self.assertTrue(author.name.startswith("Grimm"))
        self.assertEqual(author.id, 971)
        self.assertEqual(author.marcrel, 'aut')
        self.assertEqual(author.role, 'Author')
        self.assertEqual(author.birthdate, 1785)
        self.assertEqual(author.deathdate, 1863)
        self.assertEqual(author.name_and_dates, 'Grimm, Jacob, 1785-1863')
        self.assertEqual(author.webpages[0].url, 'https://en.wikipedia.org/wiki/Jacob_Grimm')
        self.assertEqual(author.aliases[0].alias, 'Grimm, Jacob Ludwig Carl')
        self.assertEqual(len(dc.subjects), 1)
        self.assertEqual(dc.subjects[0].subject, 'Fairy tales -- Germany')
        self.assertEqual(len(dc.bookshelves), 1)
        self.assertEqual(dc.bookshelves[0].bookshelf, 'DE Kinderbuch')
        self.assertEqual(dc.loccs[0].locc, 'Geography, Anthropology, Recreation: Folklore')
        self.assertEqual(dc.dcmitypes[0].id, 'Sound')


    def metadata_test2(self, dc2):
        dc2.load_from_database(self.ebook2)
        self.assertEqual('en', dc2.languages[0].id)
        self.assertEqual(len(dc2.bookshelves), 5)
        self.assertEqual(dc2.bookshelves[0].bookshelf, 'Napoleonic(Bookshelf)')
        self.assertEqual(dc2.dcmitypes[0].id, 'Text')


    def test_files(self):
        dc = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        self.files_test1(dc)
        self.files_test2(dc)

    def test_orm_files(self):
        dc = DublinCoreMapping.DublinCoreObject()
        self.files_test1(dc)
        self.files_test2(dc)

    def files_test1(self, dc):
        dc.load_from_database(self.ebook)
        self.assertTrue(dc.new_filesystem)
        self.assertEqual(len(dc.files) , 159)
        self.assertEqual(dc.files[0].archive_path, '2/0/0/5/20050/20050-readme.txt')
        self.assertEqual(dc.files[0].url, 'https://www.gutenberg.org/files/20050/20050-readme.txt')
        self.assertTrue(dc.files[0].extent, True)
        self.assertEqual(dc.files[0].hr_extent, '25\xa0kB')
        self.assertTrue(dc.files[0].modified, True)
        self.assertEqual(dc.files[0].hr_filetype, 'Readme')
        self.assertEqual(dc.files[0].encoding, None)
        self.assertEqual(dc.files[0].compression, 'none')
        self.assertEqual(dc.files[0].generated, False)
        self.assertEqual(dc.files[0].filetype, 'readme')
        self.assertTrue('Readme' in dc.filetypes)
        self.assertEqual(dc.files[0].mediatypes[-1].mimetype, 'text/plain')
        self.assertEqual(len(dc.mediatypes), 6)
        self.assertTrue('audio/ogg' in dc.mediatypes)

    def files_test2(self, dc2):
        dc2.load_from_database(self.ebook2)
        self.assertEqual(len(dc2.files) , 11)
        self.assertEqual(dc2.files[0].encoding, 'utf-8')
        self.assertEqual(dc2.files[1].compression, 'zip')
        self.assertEqual(dc2.files[2].generated, True)
        self.assertEqual(dc2.files[2].url, 'https://www.gutenberg.org/ebooks/2600.epub.images')


    def exercise(self, ebook, dc):
        dc.__init__(self.dummypool)
        dc.load_from_database(ebook)
        test = '%s%s%s%s' % (dc.title, dc.title_file_as, dc.rights,dc.rights)
        test = [lang.id for lang in dc.languages]
        test = [marc.code for marc in dc.marcs]
        test = [[alias for alias in author.aliases] for author in dc.authors]
        test = [subject for subject in dc.subjects]

    def test_10k(self):
        class DCCompat(DublinCoreMapping.DublinCoreObject):
            def __init__(self, pool):
                DublinCoreMapping.DublinCoreObject.__init__(self, session=None, pooled=True)
        dc = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        start_time = datetime.datetime.now()

        for ebook in range(5, 60005, 60):
            self.exercise(ebook, dc)
        end_time = datetime.datetime.now()
        print(' Finished 1000 dc tests. Total time: %s' % (end_time - start_time))

        start_time = datetime.datetime.now()

        for ebook in range(5, 60005, 60):
            dc = DCCompat(None)
            self.exercise(ebook, dc)
            dc.session.close()
        end_time = datetime.datetime.now()
        print(' Finished 1000 orm_dc tests. Total time: %s' % (end_time - start_time))

    def test_add_delete_files(self):
        fn = 'README.md'
        saved = False
        dc2 = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        dc2.load_files_from_database(self.ebook2)
        numfiles = len(dc2.files)
        dc2.store_file_in_database(self.ebook2, fn, 'txt')
        dc2.store_file_in_database(self.ebook2, fn, 'txt') # test over-writing
        dc2.load_files_from_database(2600)
        for file_ in dc2.files:
            if file_.archive_path == fn:
                saved = True
                break
        self.assertTrue(saved)
        dc2.remove_file_from_database(fn) # filenames are unique!
        dc2.load_files_from_database(self.ebook2)
        self.assertEqual(numfiles, len(dc2.files))
        

    def test_delete_types(self):
        fn = 'cache_for_test'  # command only remove filenames starting with 'cache'
        dc2 = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        dc2.load_files_from_database(self.ebook2)
        numfiles = len(dc2.files)
        dc2.store_file_in_database(self.ebook2, fn, 'qioo') # type is extinct
        dc2.load_files_from_database(self.ebook2)
        self.assertEqual(numfiles + 1, len(dc2.files))
        dc2.remove_filetype_from_database(self.ebook2, 'qioo')
        dc2.load_files_from_database(self.ebook2)
        self.assertEqual(numfiles, len(dc2.files))

    def test_register_coverpage(self):
        def get_cover(ebook, dc):
            dc.load_from_database(ebook)
            for marc in dc.marcs:
                if marc.code == '901':
                    return marc.text
        #ebook = 46     # tests the method, but there's no code to undo the test
        ebook = 199     # no ebook by that number
        dc = GutenbergDatabaseDublinCore.GutenbergDatabaseDublinCore(self.dummypool)
        dc.register_coverpage(ebook, 'new_cover')
        # does nothing to avoid violates foreign key constraint
        self.assertEqual(get_cover(ebook, dc), None) 
        
    def tearDown(self):
        pass
