"""
Módulo para la vista del Dashboard.
"""
import customtkinter as ctk
from datetime import datetime

from ..models.task import Status
from ..services.task_service import TaskService


class DashboardView(ctk.CTkFrame):
    """Clase para la vista del dashboard."""

    def __init__(self, master, task_service: TaskService, main_window):
        super().__init__(master, fg_color="transparent")
        self.task_service = task_service
        self.main_window = main_window

        self._create_widgets()
        self.update_view()

    def update_view(self):
        """Actualiza todos los datos de la vista."""
        self._update_dashboard_counts()
        self._update_productivity_chart()


    def _create_widgets(self) -> None:
        """Crea los widgets del dashboard."""
        # Título del dashboard
        label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)

        # Resumen de Actividades
        ctk.CTkLabel(
            self,
            text="Resumen de Actividades",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)

        # Frame para las tarjetas de resumen
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20, padx=20)

        card_config = {
            "width": 200,
            "height": 120,
            "corner_radius": 12,
            "border_width": 3,
            "fg_color": ("white", "gray10")
        }

        label_style = {
            "font": ctk.CTkFont(size=14, weight="bold"),
            "text_color": ("gray30", "gray70")
        }

        count_style = {
            "font": ctk.CTkFont(size=28, weight="bold"),
            "text_color": ("gray10", "gray90")
        }

        def create_card_click_handler(status):
            def handler(event):
                self.main_window.display_view("tasks", status)
            return handler

        # Obtener el color de acento de forma segura
        temp_button = ctk.CTkButton(self)
        accent_color = temp_button.cget("fg_color")
        temp_button.destroy()

        # Tarjeta de tareas pendientes
        pending_card = ctk.CTkFrame(cards_frame, **card_config, border_color=("#FF8C00", "#FFA500"), cursor="hand2")
        pending_card.pack_propagate(False)
        pending_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        pending_card.bind("<Button-1>", create_card_click_handler("Tareas Pendientes"))

        ctk.CTkLabel(pending_card, text="Tareas Pendientes", **label_style, cursor="hand2").pack(pady=(25, 10))
        self.pending_count = ctk.CTkLabel(pending_card, text="0", **count_style, cursor="hand2")
        self.pending_count.pack()

        # Tarjeta de tareas en curso
        in_progress_card = ctk.CTkFrame(cards_frame, **card_config, border_color=("#1E90FF", "#4169E1"), cursor="hand2")
        in_progress_card.pack_propagate(False)
        in_progress_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        in_progress_card.bind("<Button-1>", create_card_click_handler("En Curso"))

        ctk.CTkLabel(in_progress_card, text="En Curso", **label_style, cursor="hand2").pack(pady=(25, 10))
        self.overdue_count = ctk.CTkLabel(in_progress_card, text="0", **count_style, cursor="hand2")
        self.overdue_count.pack()

        # Tarjeta de tareas finalizadas
        completed_card = ctk.CTkFrame(cards_frame, **card_config, border_color=("#32CD32", "#2E8B57"), cursor="hand2")
        completed_card.pack_propagate(False)
        completed_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        completed_card.bind("<Button-1>", create_card_click_handler("Tareas Finalizadas"))

        ctk.CTkLabel(completed_card, text="Tareas Finalizadas", **label_style, cursor="hand2").pack(pady=(25, 10))
        self.completed_count = ctk.CTkLabel(completed_card, text="0", **count_style, cursor="hand2")
        self.completed_count.pack()

        cards_frame.pack_configure(padx=20, pady=15)

        # Contenedor para la barra de progreso
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(20, 10), padx=20)

        self.progress_label = ctk.CTkLabel(progress_frame, text="Progreso general: 0%", font=ctk.CTkFont(weight="bold"))
        self.progress_label.pack(anchor="w", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20, corner_radius=10, progress_color=("#4CAF50", "#2E7D32"), fg_color=("#E0E0E0", "#424242"))
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)

        # Sección de Racha de Productividad
        productivity_frame = ctk.CTkFrame(self, fg_color="transparent")
        productivity_frame.pack(fill="x", pady=(30, 20), padx=20)

        ctk.CTkLabel(productivity_frame, text="📅 Racha de Productividad", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        chart_frame = ctk.CTkFrame(productivity_frame, fg_color=("#f5f5f5", "#1a1a1a"), corner_radius=12)
        chart_frame.pack(fill="both", expand=True)

        self.chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._init_productivity_chart()

    def _update_dashboard_counts(self):
        """Actualiza los contadores del dashboard y la barra de progreso."""
        try:
            tasks = self.task_service.get_all_tasks()
            total_tasks = len(tasks)

            pending = sum(1 for task in tasks if task.status == Status.PENDING)
            completed = sum(1 for task in tasks if task.status == Status.COMPLETED)
            in_progress = sum(1 for task in tasks if task.status == Status.IN_PROGRESS)

            self.pending_count.configure(text=str(pending))
            self.completed_count.configure(text=str(completed))
            self.overdue_count.configure(text=str(in_progress))

            if total_tasks > 0:
                progress = completed / total_tasks
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Progreso general: {int(progress * 100)}%")
            else:
                self.progress_bar.set(0)
                self.progress_label.configure(text="Progreso general: 0%")

        except Exception as e:
            print(f"Error al actualizar contadores del dashboard: {e}")

    def _init_productivity_chart(self):
        """Inicializa el contenedor del gráfico de productividad."""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        self.bars_container = ctk.CTkFrame(self.chart_container, fg_color="transparent")
        self.bars_container.pack(fill="both", expand=True)

    def _update_productivity_chart(self):
        """Actualiza el gráfico de racha de productividad."""
        try:
            if not hasattr(self, 'bars_container') or not self.bars_container.winfo_exists():
                return

            for widget in self.bars_container.winfo_children():
                widget.destroy()

            completed_tasks = self.task_service.get_completed_tasks_last_week()

            if not completed_tasks:
                no_data_label = ctk.CTkLabel(self.bars_container, text="No hay datos de productividad recientes", text_color=("gray50", "gray60"), font=ctk.CTkFont(weight="bold"))
                no_data_label.pack(pady=40)
                return

            max_count = max(completed_tasks.values()) if any(completed_tasks.values()) else 1
            max_height = 150

            header_frame = ctk.CTkFrame(self.bars_container, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 15))

            ctk.CTkLabel(header_frame, text="Tareas finalizadas en los últimos 7 días", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

            total_tasks_week = sum(completed_tasks.values())
            avg_tasks = total_tasks_week / len(completed_tasks) if completed_tasks else 0

            stats_text = f"Total: {total_tasks_week} | Promedio diario: {avg_tasks:.1f}"
            ctk.CTkLabel(header_frame, text=stats_text, text_color=("gray50", "gray60"), font=ctk.CTkFont(size=12)).pack(side="right")

            chart_frame = ctk.CTkFrame(self.bars_container, fg_color=("#f5f5f5", "#1a1a1a"), corner_radius=8)
            chart_frame.pack(fill="both", expand=True, padx=0, pady=0)

            bars_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
            bars_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(20, 10))

            days_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
            days_frame.pack(side="bottom", fill="x", pady=(0, 10))

            num_days = len(completed_tasks)
            for i in range(num_days):
                bars_frame.columnconfigure(i, weight=1)
                days_frame.columnconfigure(i, weight=1)

            for i, (date, count) in enumerate(completed_tasks.items()):
                bar_height = (count / max_count) * max_height if max_count > 0 else 0
                bar_height = max(10, bar_height)

                bar_frame = ctk.CTkFrame(bars_frame, fg_color="transparent")
                bar_frame.grid(row=0, column=i, padx=4, sticky="nsew")
                bar_frame.columnconfigure(0, weight=1)

                bar_container = ctk.CTkFrame(bar_frame, fg_color="transparent")
                bar_container.pack(fill="both", expand=True)

                count_label = ctk.CTkLabel(bar_container, text=str(count) if count > 0 else "0", text_color=("black", "white"), font=ctk.CTkFont(size=12, weight="bold"))
                count_label.pack(side="top", pady=(0, 5))

                bar_color = "#4CAF50"
                bar = ctk.CTkFrame(bar_container, fg_color=bar_color, corner_radius=6, height=bar_height, width=30)
                bar.pack(side="bottom", fill="x")

                day_name = date.strftime("%a").upper()
                day_label = ctk.CTkLabel(days_frame, text=day_name, font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray30", "gray70"))
                day_label.grid(row=0, column=i, pady=(5, 0))

                date_label = ctk.CTkLabel(days_frame, text=date.strftime("%d/%m"), text_color=("gray50", "gray60"), font=ctk.CTkFont(size=11))
                date_label.grid(row=1, column=i, pady=(2, 0))

                if date == datetime.now().date():
                    day_label.configure(text_color=("#2196F3", "#64B5F6"))
                    date_label.configure(text_color=("#2196F3", "#64B5F6"))
                    bar.configure(fg_color=("#2196F3", "#64B5F6"))

                    today_label = ctk.CTkLabel(bar_frame, text="HOY", text_color=("#2196F3", "#64B5F6"), font=ctk.CTkFont(size=10, weight="bold"))
                    today_label.pack(side="top", pady=(0, 5))

                    count_label.pack_forget()
                    count_label.pack(side="top", pady=(0, 5))

        except Exception as e:
            print(f"Error al actualizar el gráfico de productividad: {e}")
