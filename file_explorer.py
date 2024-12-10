import os
import sys
import shutil
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTreeView, QFileSystemModel, QPushButton,
                            QInputDialog, QMessageBox, QLineEdit, QLabel, 
                            QFileDialog, QMenu, QDialog, QTextEdit, QShortcut,
                            QComboBox, QProgressDialog, QAbstractItemView,
                            QGroupBox, QFormLayout, QDialogButtonBox, QCheckBox,
                            QGridLayout, QToolBar, QStatusBar, QFileIconProvider)
from PyQt5.QtCore import QDir, Qt, QSize, QUrl
from PyQt5.QtGui import QImage, QPixmap, QKeySequence, QIcon
from login_dialog import LoginDialog

class PreviewDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle('文件预览')
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout(self)
        
        # 文本预览
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        
        # 图片预览
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.text_preview)
        layout.addWidget(self.image_label)
        
        self.load_preview(file_path)
    
    def load_preview(self, file_path):
        # 图片预览
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image = QImage(file_path)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(QSize(550, 350), Qt.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
                self.text_preview.hide()
                return
        
        # 文本预览
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(4000)  # 限制预览内容大小
                self.text_preview.setText(content)
                self.image_label.hide()
        except:
            self.text_preview.setText('无法预览此文件')
            self.image_label.hide()

class PropertiesDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle('文件属性')
        self.setGeometry(200, 200, 400, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 基本信息
        info_group = QGroupBox('基本信息')
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit(os.path.basename(self.file_path))
        self.name_edit.setReadOnly(True)
        info_layout.addRow('名称:', self.name_edit)
        
        self.type_label = QLabel(self.get_file_type())
        info_layout.addRow('类型:', self.type_label)
        
        self.size_label = QLabel(self.get_file_size())
        info_layout.addRow('大小:', self.size_label)
        
        self.location_edit = QLineEdit(os.path.dirname(self.file_path))
        self.location_edit.setReadOnly(True)
        info_layout.addRow('位置:', self.location_edit)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 时间信息
        time_group = QGroupBox('时间信息')
        time_layout = QFormLayout()
        
        created = time.localtime(os.path.getctime(self.file_path))
        modified = time.localtime(os.path.getmtime(self.file_path))
        accessed = time.localtime(os.path.getatime(self.file_path))
        
        time_layout.addRow('创建时间:', QLabel(time.strftime('%Y-%m-%d %H:%M:%S', created)))
        time_layout.addRow('修改时间:', QLabel(time.strftime('%Y-%m-%d %H:%M:%S', modified)))
        time_layout.addRow('访问时间:', QLabel(time.strftime('%Y-%m-%d %H:%M:%S', accessed)))
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # 权限设置
        perm_group = QGroupBox('权限设置')
        perm_layout = QGridLayout()
        
        self.read_cb = QCheckBox('读取')
        self.write_cb = QCheckBox('写入')
        self.exec_cb = QCheckBox('执行')
        
        # 获取当前权限
        stat = os.stat(self.file_path)
        mode = stat.st_mode
        
        self.read_cb.setChecked(bool(mode & 0o444))
        self.write_cb.setChecked(bool(mode & 0o222))
        self.exec_cb.setChecked(bool(mode & 0o111))
        
        perm_layout.addWidget(self.read_cb, 0, 0)
        perm_layout.addWidget(self.write_cb, 0, 1)
        perm_layout.addWidget(self.exec_cb, 0, 2)
        
        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_file_type(self):
        if os.path.isdir(self.file_path):
            return '文件夹'
        ext = os.path.splitext(self.file_path)[1].lower()
        type_map = {
            '.txt': '文本文件',
            '.doc': 'Word文档',
            '.docx': 'Word文档',
            '.pdf': 'PDF文档',
            '.jpg': 'JPEG图片',
            '.png': 'PNG图片',
            '.exe': '可执行文件'
        }
        return type_map.get(ext, f'{ext[1:].upper()}文件' if ext else '文件')
    
    def get_file_size(self):
        if os.path.isdir(self.file_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.file_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return format_size(total_size)
        return format_size(os.path.getsize(self.file_path))
    
    def accept(self):
        try:
            # 计算新的权限模式
            mode = 0
            if self.read_cb.isChecked():
                mode |= 0o444
            if self.write_cb.isChecked():
                mode |= 0o222
            if self.exec_cb.isChecked():
                mode |= 0o111
                
            # 应用新的权限
            os.chmod(self.file_path, mode)
            super().accept()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'无法修改权限: {str(e)}')

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文件资源管理器')
        
        # 设置窗口大小
        self.resize(1000, 600)
        
        # 设置最小窗口大小
        self.setMinimumSize(800, 600)
        
        # 获取屏幕几何信息
        screen = QApplication.primaryScreen().geometry()
        # 计算窗口居中位置
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到居中位置
        self.move(x, y)
        
        # 保存剪贴板中的文件路径
        self.clipboard_file = None
        
        self.history = []
        self.current_index = -1
        
        # 添加撤销/重做栈
        self.undo_stack = []
        self.redo_stack = []
        
        # 设置初始过滤器以显示驱动器
        self.initial_filter = QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives
        
        self.setup_ui()
        
        # 初始化时显示根目录（计算机）
        self.goto_root()

    def setup_ui(self):
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧快捷方式面板
        shortcut_panel = self.create_shortcut_panel()
        main_layout.addWidget(shortcut_panel)
        
        # 创建右侧主要内容布局
        content_layout = QVBoxLayout()
        
        # 添加工具栏
        self.create_toolbar()
        
        # 创建搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入文件名搜索...')
        self.search_input.setClearButtonEnabled(True)

        self.search_subdirs = QCheckBox('搜索子目录')
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_files)
        self.search_input.returnPressed.connect(self.search_files)

        search_layout.addWidget(QLabel('搜索:'))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_subdirs)
        search_layout.addWidget(search_button)
        content_layout.addLayout(search_layout)
        
        # 创建导航栏
        nav_layout = self.create_navigation_bar()
        content_layout.addLayout(nav_layout)
        
        # 创建文件系统模型和视图
        self.create_file_view()
        content_layout.addWidget(self.tree)
        
        # 创建底部按钮栏
        button_layout = self.create_button_bar()
        content_layout.addLayout(button_layout)
        
        # 创建文件类型过滤器
        filter_layout = self.create_filter_bar()
        content_layout.addLayout(filter_layout)
        
        main_layout.addLayout(content_layout)
        
        # 添加状态栏
        self.statusBar = self.statusBar()
        self.statusBar.showMessage('就绪')

    def create_shortcut_panel(self):
        shortcut_panel = QWidget()
        shortcut_layout = QVBoxLayout(shortcut_panel)
        shortcut_panel.setMaximumWidth(150)  # 限制宽度
        
        shortcuts = [
            ('桌面', os.path.expanduser('~/Desktop')),
            ('文档', os.path.expanduser('~/Documents')),
            ('下载', os.path.expanduser('~/Downloads')),
            ('图片', os.path.expanduser('~/Pictures')),
            ('音乐', os.path.expanduser('~/Music')),
            ('视频', os.path.expanduser('~/Videos')),
        ]
        
        for name, path in shortcuts:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, p=path: self.navigate_to_path(p))
            shortcut_layout.addWidget(btn)
        
        shortcut_layout.addStretch()
        return shortcut_panel

    def create_toolbar(self):
        toolbar = self.addToolBar('工具栏')
        toolbar.setMovable(False)
        
        toolbar_actions = [
            ('返回', '←', self.go_back),
            ('前进', '→', self.go_forward),
            ('刷新', '↻', self.refresh_view),
            ('根目录', '⌂', self.goto_root),
        ]
        
        for name, icon, slot in toolbar_actions:
            action = toolbar.addAction(icon)
            action.setToolTip(name)
            action.triggered.connect(slot)

    def show_context_menu(self, position):
        menu = QMenu()
        actions = [
            ('打开', self.open_file),
            ('复制', self.copy_file),
            ('粘贴', self.paste_file),
            ('删除', self.delete_file),
            ('重命名', self.rename_file),
            ('预览', self.preview_file),
            (None, None),  # 添加分隔符
            ('新建文件夹', self.create_new_folder),
            ('新建文件', self.create_new_file),
            ('属性', self.show_properties),
        ]
        
        for text, slot in actions:
            if text is None:
                menu.addSeparator()
            else:
                action = menu.addAction(text)
                action.triggered.connect(slot)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def get_selected_path(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return None
        return self.model.filePath(index)

    def open_file(self):
        file_path = self.get_selected_path()
        if file_path and os.path.isfile(file_path):
            os.startfile(file_path) if sys.platform == 'win32' else os.system(f'xdg-open "{file_path}"')

    def copy_file(self):
        self.clipboard_file = self.get_selected_path()
        if self.clipboard_file:
            QMessageBox.information(self, '复制', '文件已复制到剪贴板')

    def paste_file(self):
        if not self.clipboard_file or not os.path.exists(self.clipboard_file):
            QMessageBox.warning(self, '错误', '剪贴板为空或源文件不存在')
            return
            
        dest_path = self.get_selected_path() or QDir.rootPath()
        if os.path.isfile(dest_path):
            dest_path = os.path.dirname(dest_path)
            
        try:
            if os.path.isfile(self.clipboard_file):
                shutil.copy2(self.clipboard_file, dest_path)
            else:
                shutil.copytree(self.clipboard_file, 
                               os.path.join(dest_path, os.path.basename(self.clipboard_file)))
            QMessageBox.information(self, '成功', '文件粘贴成功')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'粘贴失败: {str(e)}')

    def delete_file(self):
        file_path = self.get_selected_path()
        if not file_path:
            return
            
        reply = QMessageBox.question(self, '确认删除', 
                                   f'确定要删除 {os.path.basename(file_path)} 吗？',
                                   QMessageBox.Yes | QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
                QMessageBox.information(self, '成功', '删除成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除失败: {str(e)}')

    def rename_file(self):
        file_path = self.get_selected_path()
        if not file_path:
            return
            
        old_name = os.path.basename(file_path)
        new_name, ok = QInputDialog.getText(self, '重命名', 
                                          '输入新名称:', 
                                          QLineEdit.Normal,
                                          old_name)
        
        if ok and new_name:
            try:
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                QMessageBox.information(self, '成功', '重命名成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'重命名失败: {str(e)}')

    def search_files(self):
        search_text = self.search_input.text().lower()
        current_path = self.model.rootPath() or QDir.rootPath()
        
        if not search_text:
            # 清除过滤器，显示所有文件
            self.model.setNameFilters([])
            self.tree.clearSelection()
            self.statusBar.showMessage('就绪')
            return
        
        try:
            # 设置状态栏
            self.statusBar.showMessage('正在搜索...')
            QApplication.processEvents()  # 让界面保持响应
            
            # 使用 QDir 进行快速搜索
            dir = QDir(current_path)
            dir.setNameFilters([f'*{search_text}*'])
            dir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)
            
            # 获取匹配的文件
            matched_files = []
            for file_info in dir.entryInfoList():
                if search_text in file_info.fileName().lower():
                    matched_files.append(file_info.filePath())
                    
                    # 获取文件的索引并选中
                    index = self.model.index(file_info.filePath())
                    self.tree.selectionModel().select(
                        index, self.tree.selectionModel().Select)
                    
                    # 每找到10个文件就更新一次界面
                    if len(matched_files) % 10 == 0:
                        self.statusBar.showMessage(f'已找到 {len(matched_files)} 个匹配项...')
                        QApplication.processEvents()
            
            # 如果有匹配项，选中第一个
            if matched_files:
                first_match = self.model.index(matched_files[0])
                self.tree.setCurrentIndex(first_match)
                self.tree.scrollTo(first_match)
                
            # 更新状态栏
            self.statusBar.showMessage(f'找到 {len(matched_files)} 个匹配项')
            
        except Exception as e:
            self.statusBar.showMessage(f'搜索出错: {str(e)}')

    def preview_file(self):
        file_path = self.get_selected_path()
        if not file_path or not os.path.isfile(file_path):
            return
            
        dialog = PreviewDialog(file_path)
        dialog.exec_()

    def create_new_folder(self):
        current_path = self.get_selected_path() or QDir.rootPath()
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)
        
        folder_name, ok = QInputDialog.getText(self, '新建文件夹', 
                                         '输入文件夹名称:')
        if ok and folder_name:
            try:
                new_path = os.path.join(current_path, folder_name)
                os.makedirs(new_path)
                QMessageBox.information(self, '成功', '文件夹创建成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'创建失败: {str(e)}')

    def create_new_file(self):
        current_path = self.get_selected_path() or QDir.rootPath()
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)
        
        file_name, ok = QInputDialog.getText(self, '新建文件', 
                                       '输入文件名称:')
        if ok and file_name:
            try:
                new_path = os.path.join(current_path, file_name)
                with open(new_path, 'w') as f:
                    pass
                QMessageBox.information(self, '成功', '文件创建成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'创建失败: {str(e)}')

    def show_properties(self):
        file_path = self.get_selected_path()
        if not file_path:
            return
        
        dialog = PropertiesDialog(file_path, self)
        dialog.exec_()

    def refresh_view(self):
        self.model.setRootPath(self.model.rootPath())
        self.update_path_display()

    def apply_filter(self, filter_text):
        if '所有文件' in filter_text:
            self.model.setNameFilters(['*'])
        else:
            # 提取号中的过滤器
            filters = filter_text[filter_text.find('(')+1:filter_text.find(')')].split()
            self.model.setNameFilters(filters)

    def copy_with_progress(self, src, dst):
        size = os.path.getsize(src)
        progress = QProgressDialog("复制文件中...", "取消", 0, size, self)
        progress.setWindowModality(Qt.WindowModal)
        
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copied = 0
                while True:
                    buf = fsrc.read(1024*1024)
                    if not buf:
                        break
                    fdst.write(buf)
                    copied += len(buf)
                    progress.setValue(copied)
                    if progress.wasCanceled():
                        break

    def add_to_history(self, path):
        self.current_index += 1
        self.history = self.history[:self.current_index]
        self.history.append(path)
        self.update_navigation_buttons()
        
    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.tree.setRootIndex(self.model.index(self.history[self.current_index]))
            self.update_path_display()
            self.update_navigation_buttons()
        
    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.tree.setRootIndex(self.model.index(self.history[self.current_index]))
            self.update_path_display()
            self.update_navigation_buttons()

    def add_to_favorites(self):
        path = self.get_selected_path()
        if path:
            self.favorites.append(path)
            self.update_favorites_menu()
        
    def create_favorites_menu(self):
        self.favorites_menu = QMenu('收藏夹')
        for path in self.favorites:
            action = self.favorites_menu.addAction(os.path.basename(path))
            action.setData(path)
            action.triggered.connect(lambda: self.goto_favorite(action.data()))

    def get_selected_paths(self):
        paths = []
        for index in self.tree.selectedIndexes():
            if index.column() == 0:  # 只处理第一列
                paths.append(self.model.filePath(index))
        return paths

    def on_double_click(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            os.startfile(file_path) if sys.platform == 'win32' else os.system(f'xdg-open "{file_path}"')
        else:
            # 如果是文件夹或驱动器，进入该目录
            if file_path:  # 如果是驱动器或文件夹
                self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)
                self.model.setRootPath(file_path)
                self.tree.setRootIndex(self.model.index(file_path))
            else:  # 如果是根目录
                self.model.setFilter(self.initial_filter)
                self.model.setRootPath('')
                self.tree.setRootIndex(self.model.index(''))
            self.add_to_history(file_path)
            self.update_path_display()

    def goto_root(self):
        # 重置模型
        self.model.setFilter(self.initial_filter)
        # 设置为空字符显示所有驱动器
        self.model.setRootPath('')
        self.tree.setRootIndex(self.model.index(''))
        self.update_path_display()
        self.add_to_history('')

    def update_path_display(self):
        current_path = self.model.filePath(self.tree.rootIndex())
        if not current_path:  # 如果是根目录
            self.path_edit.setText('计算机')
        else:
            self.path_edit.setText(current_path)

    def update_navigation_buttons(self):
        # 更新导航按钮状态
        for button in self.findChildren(QPushButton):
            if button.toolTip() == '返回':
                button.setEnabled(self.current_index > 0)
            elif button.toolTip() == '前进':
                button.setEnabled(self.current_index < len(self.history) - 1)

    def navigate_to_path(self, path):
        if path == '计算机':
            path = ''
        
        if path == '' or os.path.exists(path):  # 允许空路径（根目录）
            if path:  # 如果不是根目录
                self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)
                self.model.setRootPath(path)
                self.tree.setRootIndex(self.model.index(path))
            else:  # 如果是根目录
                self.model.setFilter(self.initial_filter)
                self.model.setRootPath('')
                self.tree.setRootIndex(self.model.index(''))
            self.add_to_history(path)
            self.update_path_display()
        else:
            QMessageBox.warning(self, '错误', '路径不存在')
            self.update_path_display()

    def create_navigation_bar(self):
        nav_layout = QHBoxLayout()
        
        # 创建导航按钮
        nav_buttons = [
            ('←', self.go_back, '返回'),
            ('→', self.go_forward, '前进'),
            ('↻', self.refresh_view, '刷新'),
            ('⌂', self.goto_root, '根目录')
        ]
        
        for text, slot, tooltip in nav_buttons:
            button = QPushButton(text)
            button.setToolTip(tooltip)
            button.clicked.connect(slot)
            nav_layout.addWidget(button)
        
        # 添加路径显示框
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.returnPressed.connect(lambda: self.navigate_to_path(self.path_edit.text()))
        nav_layout.addWidget(self.path_edit)
        
        return nav_layout

    def create_file_view(self):
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setIconProvider(QFileIconProvider())  # 添加文件图标支持
        
        # 创建树状视图
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.rootPath()))
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.on_double_click)
        
        # 设置列宽
        self.tree.setColumnWidth(0, 250)
        
        # 显示所有列
        self.tree.setHeaderHidden(False)
        
        # 启用排序
        self.tree.setSortingEnabled(True)
        self.tree.header().setSortIndicator(0, Qt.AscendingOrder)
        
        # 启用拖放
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        
        # 设置多选模式
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # 设置图标大小
        self.tree.setIconSize(QSize(16, 16))

    def create_button_bar(self):
        button_layout = QHBoxLayout()
        
        # 创建按钮
        buttons = [
            ('打开文件', self.open_file),
            ('新建文件夹', self.create_new_folder),
            ('新建文件', self.create_new_file),
            ('复制', self.copy_file),
            ('粘贴', self.paste_file),
            ('删除', self.delete_file),
            ('重命名', self.rename_file),
            ('预览', self.preview_file),
            ('属性', self.show_properties)
        ]
        
        for text, slot in buttons:
            button = QPushButton(text)
            button.clicked.connect(slot)
            button_layout.addWidget(button)
        
        return button_layout

    def create_filter_bar(self):
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['所有文件 (*.*)', '图片文件 (*.jpg *.png)', '文本文件 (*.txt)'])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(QLabel('文件类型:'))
        filter_layout.addWidget(self.filter_combo)
        return filter_layout

    def resource_path(self, relative_path):
        """ 获取资源的绝对路径 """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def main():
    app = QApplication(sys.argv)
    # 显示登录窗口
    login_dialog = LoginDialog()
    if login_dialog.exec_() != QDialog.Accepted:
        return
    
    explorer = FileExplorer()
    explorer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 