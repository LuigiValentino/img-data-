import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk 
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import piexif

class ImgDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("img-data - Editor de Metadatos de Imágenes")
        self.root.geometry("850x650")
        self.style = ttk.Style(theme='flatly')

        self.make_var = ttk.StringVar()
        self.model_var = ttk.StringVar()
        self.date_var = ttk.StringVar()
        self.resolution_x_var = ttk.StringVar()
        self.resolution_y_var = ttk.StringVar()
        self.orientation_var = ttk.StringVar()
        self.gps_lat_var = ttk.StringVar()
        self.gps_lon_var = ttk.StringVar()
        self.software_var = ttk.StringVar()
        self.author_var = ttk.StringVar()
        self.copyright_var = ttk.StringVar()
        self.load_button = ttk.Button(root, text="Cargar Imagen", command=self.load_image, width=30, bootstyle="success-outline")
        self.load_button.pack(pady=10)
        self.canvas = tk.Canvas(root, width=300, height=400) 
        self.canvas.pack(side="left", padx=50, pady=10)
        self.metadata_frame = ttk.Frame(root, padding=10)
        self.metadata_frame.pack(side="right", padx=20, pady=10)
        fields_frame = ttk.LabelFrame(self.metadata_frame, text="Modificar Metadatos", padding=20, bootstyle="info")
        fields_frame.pack(padx=10, pady=10)
        self.create_field(fields_frame, "Marca de la Cámara", self.make_var, 0)
        self.create_field(fields_frame, "Modelo", self.model_var, 1)
        self.create_field(fields_frame, "Fecha", self.date_var, 2)
        self.create_field(fields_frame, "Resolución X", self.resolution_x_var, 3)
        self.create_field(fields_frame, "Resolución Y", self.resolution_y_var, 4)
        self.create_field(fields_frame, "Orientación", self.orientation_var, 5)
        self.create_field(fields_frame, "Latitud GPS", self.gps_lat_var, 6)
        self.create_field(fields_frame, "Longitud GPS", self.gps_lon_var, 7)
        self.create_field(fields_frame, "Software", self.software_var, 8)
        self.create_field(fields_frame, "Autor", self.author_var, 9)
        self.create_field(fields_frame, "Copyright", self.copyright_var, 10)
        self.save_button = ttk.Button(self.metadata_frame, text="Guardar Metadatos", command=self.save_metadata, width=30, bootstyle="primary-outline")
        self.save_button.pack(pady=10)
        self.no_exif_label = ttk.Label(self.metadata_frame, text="", bootstyle="danger")
        self.no_exif_label.pack()

    def create_field(self, frame, label_text, var, row):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=var, width=30).grid(row=row, column=1, padx=5, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg")])
        if not file_path:
            return

        self.image_path = file_path
        image = Image.open(file_path)
        image.thumbnail((300, 400))
        self.img = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        self.load_metadata()

    def load_metadata(self):
        try:
            img = Image.open(self.image_path)
            exif_data = img.info.get('exif', None)
            
            if exif_data:
                exif_dict = piexif.load(exif_data)
                self.make_var.set(exif_dict['0th'].get(piexif.ImageIFD.Make, b'').decode(errors='ignore'))
                self.model_var.set(exif_dict['0th'].get(piexif.ImageIFD.Model, b'').decode(errors='ignore'))
                self.date_var.set(exif_dict['0th'].get(piexif.ImageIFD.DateTime, b'').decode(errors='ignore'))
                self.resolution_x_var.set(exif_dict['0th'].get(piexif.ImageIFD.XResolution, (1,1))[0])
                self.resolution_y_var.set(exif_dict['0th'].get(piexif.ImageIFD.YResolution, (1,1))[0])
                self.orientation_var.set(exif_dict['0th'].get(piexif.ImageIFD.Orientation, 1))

                gps_ifd = exif_dict.get("GPS", {})
                if gps_ifd:
                    gps_lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
                    gps_lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
                    self.gps_lat_var.set(self.convert_gps_to_degrees(gps_lat) if gps_lat else "")
                    self.gps_lon_var.set(self.convert_gps_to_degrees(gps_lon) if gps_lon else "")

                self.software_var.set(exif_dict['0th'].get(piexif.ImageIFD.Software, b'').decode(errors='ignore'))
                self.author_var.set(exif_dict['0th'].get(piexif.ImageIFD.Artist, b'').decode(errors='ignore'))
                self.copyright_var.set(exif_dict['0th'].get(piexif.ImageIFD.Copyright, b'').decode(errors='ignore'))

                self.no_exif_label.config(text="")
            else:
                self.clear_fields()
                self.no_exif_label.config(text="Advertencia: No se encontraron metadatos EXIF.")
        except Exception as e:
            print(f"Error al cargar los metadatos: {e}")
            self.no_exif_label.config(text="Error al cargar los metadatos.")

    def clear_fields(self):
        self.make_var.set("")
        self.model_var.set("")
        self.date_var.set("")
        self.resolution_x_var.set("")
        self.resolution_y_var.set("")
        self.orientation_var.set("")
        self.gps_lat_var.set("")
        self.gps_lon_var.set("")
        self.software_var.set("")
        self.author_var.set("")
        self.copyright_var.set("")

    def convert_gps_to_degrees(self, gps_data):
        degrees = gps_data[0][0] / gps_data[0][1]
        minutes = gps_data[1][0] / gps_data[1][1] / 60
        seconds = gps_data[2][0] / gps_data[2][1] / 3600
        return degrees + minutes + seconds

    def save_metadata(self):
        img = Image.open(self.image_path)
        
        try:
            exif_data = img.info.get('exif', None)
            if exif_data:
                exif_dict = piexif.load(exif_data)
                exif_dict['0th'][piexif.ImageIFD.Make] = self.make_var.get().encode('utf-8')
                exif_dict['0th'][piexif.ImageIFD.Model] = self.model_var.get().encode('utf-8')
                exif_dict['0th'][piexif.ImageIFD.DateTime] = self.date_var.get().encode('utf-8')
                exif_dict['0th'][piexif.ImageIFD.XResolution] = (int(self.resolution_x_var.get()), 1)
                exif_dict['0th'][piexif.ImageIFD.YResolution] = (int(self.resolution_y_var.get()), 1)
                exif_dict['0th'][piexif.ImageIFD.Orientation] = int(self.orientation_var.get())
                gps_ifd = exif_dict.get("GPS", {})
                if self.gps_lat_var.get() and self.gps_lon_var.get():
                    gps_ifd[piexif.GPSIFD.GPSLatitude] = self.convert_degrees_to_gps(self.gps_lat_var.get())
                    gps_ifd[piexif.GPSIFD.GPSLongitude] = self.convert_degrees_to_gps(self.gps_lon_var.get())
                exif_dict['GPS'] = gps_ifd
                exif_dict['0th'][piexif.ImageIFD.Software] = self.software_var.get().encode('utf-8')
                exif_dict['0th'][piexif.ImageIFD.Artist] = self.author_var.get().encode('utf-8')
                exif_dict['0th'][piexif.ImageIFD.Copyright] = self.copyright_var.get().encode('utf-8')
                exif_bytes = piexif.dump(exif_dict)
            else:
                exif_bytes = None
                messagebox.showwarning("Sin Metadatos EXIF", "No hay metadatos EXIF para modificar, guardando sin EXIF.")
        except Exception as e:
            exif_bytes = None
            messagebox.showerror("Error", f"Error al guardar los metadatos: {e}")

        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        
        if save_path:
            try:
                if exif_bytes:
                    img.save(save_path, "jpeg", exif=exif_bytes)
                else:
                    img.save(save_path, "jpeg")  
                messagebox.showinfo("Guardado", "La imagen ha sido guardada con éxito!")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar la imagen: {e}")

    def convert_degrees_to_gps(self, degrees_str):
        degrees = float(degrees_str)
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = (degrees - d - m / 60) * 3600
        return [(d, 1), (m, 1), (int(s * 1000), 1000)]

root = ttk.Window(themename="flatly")  
app = ImgDataApp(root)
root.mainloop()
