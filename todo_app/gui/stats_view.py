"""
Módulo para la vista de Estadísticas.
"""
import customtkinter as ctk
import pandas as pd
from io import BytesIO
from PIL import Image
from customtkinter import CTkImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ..services.statistics_service import StatisticsService
from ..models.task import Status
from datetime import timedelta

class StatsView(ctk.CTkFrame):
    """Clase para la vista de estadísticas."""

    def __init__(self, master, task_service, main_window):
        super().__init__(master, fg_color="transparent")
        self.task_service = task_service
        self.main_window = main_window
        self.statistics_service = StatisticsService()

        self._create_widgets()
        self._load_summary_stats() # Cargar estadísticas al iniciar

    def _create_widgets(self) -> None:
        """Crea los widgets de la vista de estadísticas."""
        # Layout principal con grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Título
        title_label = ctk.CTkLabel(self, text="Estadísticas de Tareas", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame para el contenido principal (tarjetas y selector)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3) # Columna para tarjetas
        content_frame.grid_columnconfigure(1, weight=1) # Columna para selector
        content_frame.grid_rowconfigure(1, weight=1)

        # --- Tarjetas de Resumen ---
        cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.summary_cards = {}
        stats_to_show = {
            "total_tasks": ("📊", "Total de Tareas"),
            "predominant_priority": ("🔥", "Prioridad Predominante"),
            "most_productive_day": ("📅", "Día más Productivo"),
            "avg_completion_time": ("⏱️", "Promedio de Finalización")
        }

        cards_frame.grid_columnconfigure((0, 1), weight=1)

        for i, (key, (icon, title)) in enumerate(stats_to_show.items()):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(cards_frame, corner_radius=10)
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            card.grid_columnconfigure(0, weight=0)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=30)).grid(row=0, column=0, rowspan=2, padx=15, pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=(0,10))
            value_label = ctk.CTkLabel(card, text="-", font=ctk.CTkFont(size=20))
            value_label.grid(row=1, column=1, sticky="w", padx=(0,10))
            self.summary_cards[key] = value_label

        # --- Selector de Gráficos ---
        selector_frame = ctk.CTkFrame(content_frame, fg_color=("gray90", "gray20"))
        selector_frame.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(selector_frame, text="Seleccionar Gráficos", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.chart_vars = {}
        self.chart_methods = {
            "Tareas por Prioridad": self.statistics_service.get_priority_chart,
            "Tareas por Estado": self.statistics_service.get_status_chart,
            "Distribución Temporal": self.statistics_service.get_temporal_distribution_chart,
            "Heatmap": self.statistics_service.get_priority_status_heatmap,
            "Torta Prioridades": self.statistics_service.get_priority_pie_chart,
            "Torta Estados": self.statistics_service.get_status_pie_chart,
            "Tendencia de Estados": self.statistics_service.get_status_trend_chart,
        }

        for name in self.chart_methods.keys():
            var = ctk.BooleanVar()
            self.chart_vars[name] = var
            chk = ctk.CTkCheckBox(selector_frame, text=name, variable=var)
            chk.pack(pady=5, padx=10, anchor="w")
        
        # Marcar los dos primeros por defecto
        self.chart_vars["Tareas por Prioridad"].set(True)
        self.chart_vars["Tareas por Estado"].set(True)

        generate_btn = ctk.CTkButton(selector_frame, text="Generar Gráficos", command=self._generate_charts)
        generate_btn.pack(pady=20, padx=10, anchor="s")


    def _load_summary_stats(self):
        tasks = self.task_service.get_all_tasks()
        stats = self.statistics_service.get_summary_stats(tasks)
        for key, value in stats.items():
            if key in self.summary_cards:
                self.summary_cards[key].configure(text=str(value))


    def _generate_charts(self):

        tasks = self.task_service.get_all_tasks()
        if not tasks:
            ctk.CTkLabel(self.charts_container, text="No hay tareas para generar estadísticas.").pack(pady=20)
            return

        # Generar y mostrar los gráficos seleccionados
        for name, var in self.chart_vars.items():
            if var.get():
                chart_method = self.chart_methods[name]
                fig = chart_method(tasks)
                self._display_chart(fig, name)


    def _display_chart(self, fig, title: str):
        if fig is None:
            return

        # Crear una nueva ventana emergente para el gráfico
        chart_window = ctk.CTkToplevel(self)
        chart_window.title(title)
        chart_window.geometry("800x600")
        chart_window.grab_set() # Hacerla modal

        # Crear el lienzo de Matplotlib para Tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Añadir la barra de herramientas de navegación
        toolbar = NavigationToolbar2Tk(canvas, chart_window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
