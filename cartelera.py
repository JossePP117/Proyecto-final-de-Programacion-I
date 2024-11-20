import sqlite3
from tkinter import Tk, Button, Label, Frame, Canvas, Entry, StringVar, OptionMenu, Scrollbar
from PIL import Image, ImageTk

class Base_datos:

    def __init__(self, db_direccion):
        self.db_direccion = db_direccion

    def obtener_peliculas(self, filtro=None, valor=None):
        try:
            conector = sqlite3.connect(self.db_direccion)
            cursor = conector.cursor()

            # Consulta adaptativa
            if filtro and valor:
                cursor.execute(
                    f"SELECT nombre_pelicula, categoria, año_lanzamiento, duracion, sinopsis, portada FROM peliculas WHERE {filtro} = ?", (valor,),
                )
            else:
                cursor.execute(
                    "SELECT nombre_pelicula, categoria, año_lanzamiento, duracion, sinopsis, portada FROM peliculas"
                )

            peliculas = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al acceder a la base de datos: {e}")
            peliculas = []
        finally:
            conector.close()

        return peliculas

class Cartelera:
    def __init__(self):
        self.ventana = Tk()
        self.ventana.title("Cartelera de Películas")
        self.ventana.geometry("1000x600")
        self.bd = Base_datos("Cartelera_peliculas.db")
        self.filtro = StringVar(value="Todos")
        self.contenedor_peliculas = None
        self.no_resultados_label = None
        self.imagen_defecto = "imagenes de peliculas\imagen no disponible.png"
        self.iniciar_ventana()

    def cargar_imagen(self, portada):
        try:
            img = Image.open(portada)
        except FileNotFoundError:
            img = Image.open(self.imagen_defecto)
        img = img.resize((150, 200))
        return ImageTk.PhotoImage(img)

    def mostrar_peliculas(self, peliculas):
        if self.contenedor_peliculas:
            self.contenedor_peliculas.destroy()

        self.contenedor_peliculas = Frame(self.ventana)
        self.contenedor_peliculas.pack(fill="both", expand=True)

        # Crear un canvas con scrollbar
        canvas = Canvas(self.contenedor_peliculas)
        scrollbar = Scrollbar(self.contenedor_peliculas, orient="vertical", command=canvas.yview)
        frame_contenido = Frame(canvas)

        frame_contenido.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not peliculas:
            self.no_resultados_label = Label(
                frame_contenido,
                text="No se encontraron resultados.",
                fg="red",
                font=("Arial", 14),
            )
            self.no_resultados_label.pack(pady=20)
            return

        for pelicula in peliculas:
            nombre, categoria, año, duracion, sinopsis, portada = pelicula
            frame_pelicula = Frame(frame_contenido, bd=2, relief="groove", padx=10, pady=10)
            frame_pelicula.pack(pady=5, fill="x")

            # Portada
            img = self.cargar_imagen(portada)
            label_img = Label(frame_pelicula, image=img)
            label_img.image = img
            label_img.pack(side="left", padx=10)

            # Información de la película
            label_info = Label(
                frame_pelicula,
                text=f"{nombre}\nCategoría: {categoria}\nDuración: {duracion} min\nAño: {año}\nSinopsis: {sinopsis}",
                justify="left",
                anchor="w",
            )
            label_info.pack(side="left", fill="x", expand=True)

    def buscar_peliculas(self, filtro, entrada):
        valor = entrada.get().strip()
        filtro_bd = None if filtro == "Todos" else filtro

        # Validar filtro
        if filtro != "Todos" and not valor:
            self.mostrar_peliculas([])
            return

        peliculas = self.bd.obtener_peliculas(filtro_bd, valor)
        self.mostrar_peliculas(peliculas)

    def iniciar_ventana(self):
        # Menú de búsqueda
        frame_menu = Frame(self.ventana, bd=2, relief="groove", pady=10)
        frame_menu.pack(fill="x")

        Label(frame_menu, text="Buscar por:").pack(side="left", padx=5)
        opciones = ["Todos", "categoria", "año_lanzamiento"]
        OptionMenu(frame_menu, self.filtro, *opciones).pack(side="left", padx=5)

        Label(frame_menu, text="Valor:").pack(side="left", padx=5)
        entrada = Entry(frame_menu)
        entrada.pack(side="left", padx=5)

        Button(
            frame_menu,
            text="Buscar",
            command=lambda: self.buscar_peliculas(self.filtro.get(), entrada),
        ).pack(side="left", padx=5)
        Button(
            frame_menu,
            text="Mostrar Todo",
            command=lambda: self.buscar_peliculas("Todos", entrada),
        ).pack(side="left", padx=5)

        # Contenedor para las películas
        peliculas = self.bd.obtener_peliculas()
        self.mostrar_peliculas(peliculas)

        self.ventana.mainloop()

