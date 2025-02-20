import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from typing import List, Set

# Intentar importar tkinterdnd2
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DNDFILES_AVAILABLE = True
except ImportError:
    DNDFILES_AVAILABLE = False
    
class SourceTreeGenerator(TkinterDnD.Tk if DNDFILES_AVAILABLE else tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Source Tree Generator")
        self.geometry("800x600")
        self.configure(padx=20, pady=20)

        # Configurar el drag & drop solo si está disponible
        if DNDFILES_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.handle_drop)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self)
        
        # Ruta actual
        self.path_frame = ttk.LabelFrame(self.main_frame, text="Working Directory", padding="10")
        self.current_path = tk.StringVar(value=os.getcwd())
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.current_path, width=60)
        self.browse_button = ttk.Button(self.path_frame, text="Browse", command=self.browse_directory)
        
        # Configuración
        self.config_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")
        
        # Extensiones
        self.extensions_label = ttk.Label(self.config_frame, text="Extensions to include (comma-separated):")
        self.extensions = tk.StringVar(value="*.py,*.cpp,*.h")
        self.extensions_entry = ttk.Entry(self.config_frame, textvariable=self.extensions, width=40)
        
        # Carpetas excluidas
        self.exclude_label = ttk.Label(self.config_frame, text="Folders to exclude (comma-separated):")
        self.exclude_dirs = tk.StringVar(value="__pycache__,venv,.git")
        self.exclude_entry = ttk.Entry(self.config_frame, textvariable=self.exclude_dirs, width=40)
        
        # Botón de generación
        self.generate_button = ttk.Button(
            self.main_frame, 
            text="Generate Documentation", 
            command=self.generate_documentation
        )
        
        # Área de log
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Log", padding="10")
        self.log_text = tk.Text(self.log_frame, height=15, width=70)
        self.log_scroll = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll.set)

        # Mensaje de drag & drop
        if DNDFILES_AVAILABLE:
            self.dnd_label = ttk.Label(
                self.main_frame, 
                text="You can drag a folder here",
                font=('Arial', 10, 'italic')
            )
        else:
            self.dnd_label = ttk.Label(
                self.main_frame,
                text="To enable drag & drop: pip install tkinterdnd2",
                foreground='red'
            )

    def create_layout(self):
        # Layout principal
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ruta
        self.path_frame.pack(fill=tk.X, pady=(0, 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.browse_button.pack(side=tk.LEFT)
        
        # Configuración
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        self.extensions_label.pack(anchor=tk.W, pady=(0, 5))
        self.extensions_entry.pack(fill=tk.X, pady=(0, 10))
        self.exclude_label.pack(anchor=tk.W, pady=(0, 5))
        self.exclude_entry.pack(fill=tk.X)
        
        # Botón y mensaje de drag & drop
        self.generate_button.pack(pady=10)
        self.dnd_label.pack(pady=(0, 10))
        
        # Log
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def handle_drop(self, event):
        # Obtener la ruta arrastrada
        file_path = event.data
        
        # En Windows, la ruta viene con {}
        if sys.platform == 'win32':
            file_path = file_path.strip('{}')
        
        if os.path.isdir(file_path):
            self.current_path.set(file_path)
            self.log_message(f"Directory changed to: {file_path}")
        else:
            messagebox.showwarning(
                "Error", 
                "Please drag a valid folder."
            )

    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.current_path.get(),
            title="Select Directory"
        )
        if directory:
            self.current_path.set(directory)
            self.log_message(f"Directory changed to: {directory}")

    def log_message(self, message: str):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def get_extension_list(self) -> List[str]:
        return [ext.strip() for ext in self.extensions.get().split(',') if ext.strip()]

    def get_exclude_dirs(self) -> Set[str]:
        return {dir.strip() for dir in self.exclude_dirs.get().split(',') if dir.strip()}

    def generate_documentation(self):
        root_dir = self.current_path.get()
        if not os.path.isdir(root_dir):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        output_dir = os.path.join(root_dir, "documentation")
        os.makedirs(output_dir, exist_ok=True)

        source_file = os.path.join(output_dir, "source.txt")
        tree_file = os.path.join(output_dir, "tree_structure.txt")

        self.log_message("Starting documentation generation...")
        self.log_message(f"Root directory: {root_dir}")
        self.log_message(f"Output files:\n- {source_file}\n- {tree_file}")

        try:
            with open(source_file, 'w', encoding='utf-8') as sf, \
                 open(tree_file, 'w', encoding='utf-8') as tf:
                self._process_directory(root_dir, "", sf, tf)
            
            self.log_message("Documentation generated successfully!")
            messagebox.showinfo(
                "Success", 
                f"Documentation generated in:\n{output_dir}"
            )
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error generating documentation:\n{str(e)}")

    def _process_directory(self, current_dir: str, indent: str, source_file, tree_file):
        dir_name = os.path.basename(current_dir)
        rel_path = os.path.relpath(current_dir, self.current_path.get())
        
        # Escribir nombre del directorio
        source_file.write(f"{indent}{rel_path}/\n")
        tree_file.write(f"{indent}{rel_path}/\n")
        
        # Procesar archivos
        files = []
        for ext in self.get_extension_list():
            for file in os.listdir(current_dir):
                if file.endswith(ext.replace('*', '')):
                    files.append(file)

        # Ordenar archivos alfabéticamente
        files.sort()
        
        for file in files:
            file_path = os.path.join(current_dir, file)
            if os.path.isfile(file_path):
                # Escribir en tree_structure.txt
                tree_file.write(f"{indent}├── {file}\n")
                
                # Escribir en source.txt
                source_file.write(f"{indent}- {file}\n")
                source_file.write("---\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_file.write(f.read())
                except Exception as e:
                    source_file.write(f"Error reading file: {str(e)}\n")
                source_file.write("\n---\n\n")
                
                self.log_message(f"Processed: {file}")

        # Procesar subdirectorios
        subdirs = [d for d in os.listdir(current_dir) 
                  if os.path.isdir(os.path.join(current_dir, d)) 
                  and d not in self.get_exclude_dirs()]
        subdirs.sort()
        
        for subdir in subdirs:
            subdir_path = os.path.join(current_dir, subdir)
            self._process_directory(subdir_path, indent + "  ", source_file, tree_file)

if __name__ == "__main__":
    app = SourceTreeGenerator()
    if not DNDFILES_AVAILABLE:
        app.log_message("WARNING: Drag & Drop not available. Install tkinterdnd2 with: pip install tkinterdnd2")
    app.mainloop()