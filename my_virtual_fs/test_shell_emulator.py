import unittest
from unittest.mock import patch, MagicMock
import os
import tarfile
import json
import io
from emulator import ShellEmulator # Импортируем класс ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.tar_path = 'test.tar'
        self.log_path = 'test_log.json'

        # Создание tar-архива для тестов
        with tarfile.open(self.tar_path, 'w') as tar:
            tarinfo = tarfile.TarInfo(name="file1.txt")
            tarinfo.size = len("Hello, World!\n")
            tar.addfile(tarinfo, io.BytesIO(b"Hello, World!\n"))
            tarinfo = tarfile.TarInfo(name="dir1/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)
            tarinfo = tarfile.TarInfo(name="dir1/file2.txt")
            tarinfo.size = len("Content of file2.txt\n")
            tar.addfile(tarinfo, io.BytesIO(b"Content of file2.txt\n"))

        self.emulator = ShellEmulator(self.tar_path, self.log_path)

    def tearDown(self):
        os.remove(self.tar_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    @patch('builtins.print')
    def test_ls_root(self, mock_print):
        self.emulator.ls()
        mock_print.assert_called_once_with("file1.txt\ndir1")

    @patch('builtins.print')
    def test_ls_dir1(self, mock_print):
        self.emulator.cd('dir1')
        self.emulator.ls()
        mock_print.assert_called_once_with("file2.txt")

    @patch('builtins.print')
    def test_cd_root(self, mock_print):
        self.emulator.cd('dir1')
        self.emulator.cd('/')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_dir1(self, mock_print):
        self.emulator.cd('dir1')
        # Вызываем ls, чтобы обновить self.emulator.current_dir после cd dir1
        self.emulator.ls()
        self.assertEqual(self.emulator.current_dir, 'dir1/')

    @patch('builtins.print')
    def test_cd_parent(self, mock_print):
        self.emulator.cd('dir1')
        self.emulator.cd('..')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_nonexistent(self, mock_print):
        self.emulator.cd('nonexistent')
        mock_print.assert_called_once_with("cd: no such file or directory: nonexistent")

    @patch('builtins.print')
    @patch('os.getlogin', return_value='testuser')
    def test_whoami(self, mock_getlogin, mock_print):
        self.emulator.whoami()
        mock_print.assert_called_once_with('testuser')

    @patch('builtins.print')
    def test_tac_file(self, mock_print):
        self.emulator.tac(['file1.txt'])
        mock_print.assert_has_calls([
            unittest.mock.call("\n--- file1.txt ---\n"),
            unittest.mock.call("Hello, World!")
        ])


    @patch('builtins.print')
    def test_tac_directory(self, mock_print):
        self.emulator.tac(['dir1'])
        mock_print.assert_called_once_with("Нельзя так делать: нельзя использовать tac для директории.")

    @patch('builtins.print')
    def test_tac_nonexistent(self, mock_print):
        self.emulator.tac(['nonexistent.txt'])
        mock_print.assert_called_once_with("tac: nonexistent.txt: No such file")

    @patch('builtins.print')
    @patch('sys.exit') # Замена sys.exit для предотвращения завершения тестов
    def test_exit(self, mock_exit, mock_print):
        self.emulator.exit() # Вызываем метод exit

        # Проверяем, что print был вызван с правильным сообщением
        mock_print.assert_called_once_with("Exiting...")
        
        # Проверяем, что exit был вызван
        mock_exit.assert_called_once_with(0) # Указываем, что exit был вызван с кодом 0



if __name__ == '__main__':
    unittest.main()
