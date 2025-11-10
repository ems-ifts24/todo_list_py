"""
Servicio para generar y manejar las imágenes de los gráficos para la GUI.
"""
import pandas as pd
from io import BytesIO
from typing import List
from datetime import timedelta
from datetime import timedelta
import matplotlib
matplotlib.use('Agg') # Usar backend no interactivo, SOLUCIONA EL TCLERROR
import matplotlib.pyplot as plt

from .graphics_service import GraphicsService
from ..models.task import Task, Priority, Status

class StatisticsService:
    def __init__(self):
        # Usamos una instancia de GraphicsService para la lógica de ploteo
        self.graphics_service = GraphicsService()

    def _tasks_to_dataframe(self, tasks: List[Task]) -> pd.DataFrame:
        """Convierte una lista de tareas a un DataFrame de pandas."""
        if not tasks:
            return pd.DataFrame()
        
        df = pd.DataFrame([t.to_dict() for t in tasks])
        # Asegurarse de que las columnas de fecha son datetime
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['created_date'] = df['created_at'].dt.date
            df['created_month'] = df['created_at'].dt.to_period('M')
            df['created_week'] = df['created_at'].dt.to_period('W')
        if 'updated_at' in df.columns:
            df['updated_at'] = pd.to_datetime(df['updated_at'])
        
        return df

    def get_summary_stats(self, tasks: List[Task]) -> dict:
        """Calcula estadísticas de resumen sobre las tareas."""
        df = self._tasks_to_dataframe(tasks)
        if df.empty:
            return {
                "total_tasks": 0,
                "predominant_priority": "N/A",
                "most_productive_day": "N/A",
                "avg_completion_time": "N/A"
            }

        total_tasks = len(df)

        predominant_priority = df['priority'].mode()[0] if not df['priority'].empty else "N/A"

        completed_tasks = df[df['status'] == 'FINALIZADA'].copy()
        if not completed_tasks.empty:
            completed_tasks['completion_time'] = (completed_tasks['updated_at'] - completed_tasks['created_at']).dt.total_seconds()
            avg_completion_seconds = completed_tasks['completion_time'].mean()
            # Formatear para mostrar horas, minutos y segundos de forma legible
            if pd.notna(avg_completion_seconds):
                secs = int(avg_completion_seconds)
                hours, remainder = divmod(secs, 3600)
                minutes, seconds = divmod(remainder, 60)
                avg_completion_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                avg_completion_time = "N/A"
            
            most_productive_day = completed_tasks['updated_at'].dt.date.mode()[0].strftime('%d/%m/%Y') if not completed_tasks.empty else "N/A"
        else:
            avg_completion_time = "N/A"
            most_productive_day = "N/A"

        return {
            "total_tasks": total_tasks,
            "predominant_priority": predominant_priority,
            "most_productive_day": most_productive_day,
            "avg_completion_time": avg_completion_time
        }

    def get_priority_chart(self, tasks: List[Task]) -> plt.Figure:
        """Genera el gráfico de tareas por prioridad y lo devuelve como imagen."""
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        self.graphics_service._subplot_tasks_by_priority(df, ax)
        
        return fig

    def get_status_chart(self, tasks: List[Task]) -> plt.Figure:
        """Genera el gráfico de tareas por estado y lo devuelve como imagen."""
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None

        fig, ax = plt.subplots(figsize=(10, 6))
        self.graphics_service._subplot_tasks_by_status(df, ax)
        
        return fig

    def get_temporal_distribution_chart(self, tasks: List[Task]) -> plt.Figure:
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        fig, ax = plt.subplots(figsize=(12, 6))
        self.graphics_service._subplot_temporal_distribution(df, ax)
        return fig

    def get_priority_status_heatmap(self, tasks: List[Task]) -> plt.Figure:
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        fig, ax = plt.subplots(figsize=(10, 6))
        self.graphics_service._subplot_priority_vs_status_heatmap(df, ax)
        return fig

    def get_priority_pie_chart(self, tasks: List[Task]) -> plt.Figure:
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        fig, ax = plt.subplots(figsize=(10, 8))
        self.graphics_service._subplot_priority_pie_chart(df, ax)
        return fig

    def get_status_pie_chart(self, tasks: List[Task]) -> plt.Figure:
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        fig, ax = plt.subplots(figsize=(10, 8))
        self.graphics_service._subplot_status_pie_chart(df, ax)
        return fig

    def get_status_trend_chart(self, tasks: List[Task]) -> plt.Figure:
        df = self._tasks_to_dataframe(tasks)
        if df.empty: return None
        fig, ax = plt.subplots(figsize=(14, 6))
        self.graphics_service._subplot_status_trend_over_time(df, ax)
        return fig