"""
Servicio para generar gráficos estadísticos de tareas.
Utiliza pandas, matplotlib y seaborn para visualización de datos.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns


class GraphicsService:
    """Servicio para generar gráficos de análisis de tareas."""
    
    # Configuración de colores para prioridades
    PRIORITY_COLORS = {
        'ALTA': '#e74c3c',      # Rojo
        'MEDIA': '#f39c12',     # Naranja
        'BAJA': '#2ecc71'       # Verde
    }
    
    # Configuración de colores para estados
    STATUS_COLORS = {
        'PENDIENTE': '#95a5a6',     # Gris
        'EN CURSO': '#3498db',      # Azul
        'FINALIZADA': '#27ae60'     # Verde oscuro
    }
    
    def __init__(self):
        """Inicializa el servicio de gráficos."""
        # Configurar estilo de seaborn
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def _load_tasks_from_file(self, file_path: str) -> pd.DataFrame:
        """Carga tareas desde un archivo JSON y las convierte a DataFrame.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
            
        Returns:
            DataFrame con las tareas cargadas
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        # Convertir a DataFrame
        df = pd.DataFrame(tasks)
        
        # Convertir fechas a datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        
        # Extraer información temporal
        df['created_date'] = df['created_at'].dt.date
        df['created_month'] = df['created_at'].dt.to_period('M')
        df['created_week'] = df['created_at'].dt.to_period('W')
        
        return df
    
    def plot_tasks_by_priority(self, file_path: str) -> None:
        """Genera gráfico de barras verticales: Tareas por Prioridad.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Contar tareas por prioridad
        priority_counts = df['priority'].value_counts()
        
        # Ordenar por el orden deseado
        priority_order = ['ALTA', 'MEDIA', 'BAJA']
        priority_counts = priority_counts.reindex(priority_order, fill_value=0)
        
        # Crear gráfico
        plt.figure(figsize=(10, 6))
        colors = [self.PRIORITY_COLORS[p] for p in priority_counts.index]
        bars = plt.bar(priority_counts.index, priority_counts.values, color=colors, alpha=0.8, edgecolor='black')
        
        # Agregar valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.title('Distribución de Tareas por Prioridad', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Prioridad', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad de Tareas', fontsize=12, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_tasks_by_status(self, file_path: str) -> None:
        """Genera gráfico de barras horizontales: Tareas por Estado.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Contar tareas por estado
        status_counts = df['status'].value_counts()
        
        # Ordenar por el orden deseado
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        status_counts = status_counts.reindex(status_order, fill_value=0)
        
        # Crear gráfico
        plt.figure(figsize=(10, 6))
        colors = [self.STATUS_COLORS[s] for s in status_counts.index]
        bars = plt.barh(status_counts.index, status_counts.values, color=colors, alpha=0.8, edgecolor='black')
        
        # Agregar valores al final de las barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {int(width)}',
                    ha='left', va='center', fontweight='bold')
        
        plt.title('Distribución de Tareas por Estado', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Cantidad de Tareas', fontsize=12, fontweight='bold')
        plt.ylabel('Estado', fontsize=12, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_temporal_distribution(self, file_path: str) -> None:
        """Genera histograma: Distribución Temporal de Tareas.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Histograma por semana
        n, bins, patches = ax.hist(df['created_at'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')
        
        # Agregar valores sobre las barras (solo si hay espacio)
        for i, (count, patch) in enumerate(zip(n, patches)):
            if count > 0:  # Solo mostrar si hay datos
                height = patch.get_height()
                ax.text(patch.get_x() + patch.get_width()/2., height,
                        f'{int(count)}',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Formatear fechas en el eje X como DD-MM-YYYY
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        ax.set_title('Distribución Temporal de Creación de Tareas', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Fecha de Creación', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cantidad de Tareas', fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_priority_vs_status_heatmap(self, file_path: str) -> None:
        """Genera heatmap: Relación Prioridad vs Estado.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Crear tabla cruzada
        cross_tab = pd.crosstab(df['priority'], df['status'])
        
        # Ordenar filas y columnas
        priority_order = ['ALTA', 'MEDIA', 'BAJA']
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        cross_tab = cross_tab.reindex(index=priority_order, columns=status_order, fill_value=0)
        
        # Crear gráfico
        plt.figure(figsize=(10, 6))
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Cantidad de Tareas'},
                   linewidths=1, linecolor='black')
        
        plt.title('Relación entre Prioridad y Estado de Tareas', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Estado', fontsize=12, fontweight='bold')
        plt.ylabel('Prioridad', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_priority_pie_chart(self, file_path: str) -> None:
        """Genera gráfico de torta: Proporción de Tareas por Prioridad.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Contar tareas por prioridad
        priority_counts = df['priority'].value_counts()
        
        # Crear gráfico
        plt.figure(figsize=(10, 8))
        colors = [self.PRIORITY_COLORS[p] for p in priority_counts.index]
        
        # Función personalizada para mostrar porcentaje y cantidad
        def autopct_format(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f'{pct:.1f}%\n({absolute})'
        
        wedges, texts, autotexts = plt.pie(
            priority_counts.values,
            labels=priority_counts.index,
            colors=colors,
            autopct=lambda pct: autopct_format(pct, priority_counts.values),
            startangle=90,
            explode=[0.05] * len(priority_counts),
            shadow=True
        )
        
        # Mejorar formato de texto
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        plt.title('Proporción de Tareas por Prioridad', fontsize=14, fontweight='bold', pad=20)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    
    def plot_status_pie_chart(self, file_path: str) -> None:
        """Genera gráfico de torta: Proporción de Tareas por Estado.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Contar tareas por estado
        status_counts = df['status'].value_counts()
        
        # Crear gráfico
        plt.figure(figsize=(10, 8))
        colors = [self.STATUS_COLORS[s] for s in status_counts.index]
        
        # Función personalizada para mostrar porcentaje y cantidad
        def autopct_format(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f'{pct:.1f}%\n({absolute})'
        
        wedges, texts, autotexts = plt.pie(
            status_counts.values,
            labels=status_counts.index,
            colors=colors,
            autopct=lambda pct: autopct_format(pct, status_counts.values),
            startangle=90,
            explode=[0.05] * len(status_counts),
            shadow=True
        )
        
        # Mejorar formato de texto
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        plt.title('Proporción de Tareas por Estado', fontsize=14, fontweight='bold', pad=20)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    
    def plot_status_trend_over_time(self, file_path: str) -> None:
        """Genera stackplot: Tendencia de Estados en el Tiempo.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
        """
        df = self._load_tasks_from_file(file_path)
        
        # Agrupar por semana y estado
        df_grouped = df.groupby(['created_week', 'status']).size().unstack(fill_value=0)
        
        # Ordenar columnas
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        df_grouped = df_grouped.reindex(columns=status_order, fill_value=0)
        
        # Crear gráfico
        plt.figure(figsize=(14, 6))
        
        # Convertir índice a string para mejor visualización
        x = range(len(df_grouped))
        colors = [self.STATUS_COLORS[s] for s in df_grouped.columns]
        
        plt.stackplot(x, 
                     [df_grouped[col].values for col in df_grouped.columns],
                     labels=df_grouped.columns,
                     colors=colors,
                     alpha=0.8)
        
        plt.title('Tendencia de Estados de Tareas en el Tiempo', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Semana de Creación', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad de Tareas (Acumulado)', fontsize=12, fontweight='bold')
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(axis='y', alpha=0.3)
        
        # Configurar etiquetas del eje X (mostrar algunas semanas)
        step = max(1, len(df_grouped) // 10)
        plt.xticks(x[::step], [str(w) for w in df_grouped.index[::step]], rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_multiple_charts(self, file_path: str, chart_indices: List[int]) -> None:
        """Muestra 4 gráficos juntos en una cuadrícula 2x2.
        
        Args:
            file_path: Ruta del archivo JSON con las tareas
            chart_indices: Lista de índices de gráficos a mostrar (1-7)
        """
        if len(chart_indices) != 4:
            raise ValueError("Se deben seleccionar exactamente 4 gráficos")
        
        df = self._load_tasks_from_file(file_path)
        total_tasks = len(df)
        
        # Crear figura con subplots y márgenes ajustados
        fig = plt.figure(figsize=(16, 15))  # Un poco más alto
        
        # Añadir título general con el total de registros
        fig.suptitle(
            f'Dashboard de Análisis de Tareas\nTotal de registros: {total_tasks:,}'.replace(',', '.'), 
            fontsize=16, 
            fontweight='bold',
            y=0.98  # Un poco más arriba del borde superior
        )
        
        # Definir la cuadrícula con márgenes personalizados
        # left, right, top, bottom, wspace, hspace
        gs = fig.add_gridspec(
            nrows=2, 
            ncols=2,
            left=0.05,    # Margen izquierdo reducido
            right=0.97,   # Margen derecho reducido
            top=0.90,     # Margen superior ajustado para el título (aumentado para más espacio)
            bottom=0.05,  # Margen inferior aumentado
            hspace=0.35,  # Espacio horizontal entre filas
            wspace=0.2    # Espacio vertical entre columnas
        )
        
        # Crear los ejes con la cuadrícula
        axes = [
            fig.add_subplot(gs[0, 0]),
            fig.add_subplot(gs[0, 1]),
            fig.add_subplot(gs[1, 0]),
            fig.add_subplot(gs[1, 1])
        ]
        
        # Mapeo de índices a funciones de gráficos
        chart_functions = {
            1: self._subplot_tasks_by_priority,
            2: self._subplot_tasks_by_status,
            3: self._subplot_temporal_distribution,
            4: self._subplot_priority_vs_status_heatmap,
            5: self._subplot_priority_pie_chart,
            6: self._subplot_status_pie_chart,
            7: self._subplot_status_trend_over_time
        }
        
        # Generar cada gráfico
        for idx, chart_idx in enumerate(chart_indices):
            if chart_idx in chart_functions:
                chart_functions[chart_idx](df, axes[idx])
        
        plt.show()
    
    # Métodos auxiliares para subplots
    
    def _subplot_tasks_by_priority(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de tareas por prioridad."""
        priority_counts = df['priority'].value_counts()
        priority_order = ['ALTA', 'MEDIA', 'BAJA']
        priority_counts = priority_counts.reindex(priority_order, fill_value=0)
        
        colors = [self.PRIORITY_COLORS[p] for p in priority_counts.index]
        bars = ax.bar(priority_counts.index, priority_counts.values, color=colors, alpha=0.8, edgecolor='black')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Tareas por Prioridad', fontweight='bold')
        ax.set_xlabel('Prioridad', fontweight='bold')
        ax.set_ylabel('Cantidad', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
    
    def _subplot_tasks_by_status(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de tareas por estado."""
        status_counts = df['status'].value_counts()
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        status_counts = status_counts.reindex(status_order, fill_value=0)
        
        colors = [self.STATUS_COLORS[s] for s in status_counts.index]
        bars = ax.barh(status_counts.index, status_counts.values, color=colors, alpha=0.8, edgecolor='black')
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {int(width)}', ha='left', va='center', fontweight='bold')
        
        ax.set_title('Tareas por Estado', fontweight='bold')
        ax.set_xlabel('Cantidad', fontweight='bold')
        ax.set_ylabel('Estado', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
    
    def _subplot_temporal_distribution(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de distribución temporal."""
        n, bins, patches = ax.hist(df['created_at'], bins=20, color='#3498db', alpha=0.7, edgecolor='black')
        
        # Agregar valores sobre las barras (solo las más altas para no saturar)
        max_height = max(n)
        for i, (count, patch) in enumerate(zip(n, patches)):
            if count > max_height * 0.3:  # Solo mostrar si es significativo
                height = patch.get_height()
                ax.text(patch.get_x() + patch.get_width()/2., height,
                       f'{int(count)}',
                       ha='center', va='bottom', fontsize=7, fontweight='bold')
        
        # Formatear fechas en el eje X como DD-MM-YYYY
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        ax.set_title('Distribución Temporal', fontweight='bold')
        ax.set_xlabel('Fecha de Creación', fontweight='bold')
        ax.set_ylabel('Cantidad', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    def _subplot_priority_vs_status_heatmap(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de heatmap prioridad vs estado."""
        cross_tab = pd.crosstab(df['priority'], df['status'])
        priority_order = ['ALTA', 'MEDIA', 'BAJA']
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        cross_tab = cross_tab.reindex(index=priority_order, columns=status_order, fill_value=0)
        
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Cantidad'},
                   linewidths=1, linecolor='black', ax=ax)
        ax.set_title('Prioridad vs Estado', fontweight='bold')
        ax.set_xlabel('Estado', fontweight='bold')
        ax.set_ylabel('Prioridad', fontweight='bold')
    
    def _subplot_priority_pie_chart(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de gráfico de torta por prioridad."""
        priority_counts = df['priority'].value_counts()
        colors = [self.PRIORITY_COLORS[p] for p in priority_counts.index]
        
        # Función personalizada para mostrar porcentaje y cantidad
        def autopct_format(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f'{pct:.1f}%\n({absolute})'
        
        wedges, texts, autotexts = ax.pie(
            priority_counts.values,
            labels=priority_counts.index,
            colors=colors,
            autopct=lambda pct: autopct_format(pct, priority_counts.values),
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Proporción por Prioridad', fontweight='bold')
    
    def _subplot_status_pie_chart(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de gráfico de torta por estado."""
        status_counts = df['status'].value_counts()
        colors = [self.STATUS_COLORS[s] for s in status_counts.index]
        
        # Función personalizada para mostrar porcentaje y cantidad
        def autopct_format(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f'{pct:.1f}%\n({absolute})'
        
        wedges, texts, autotexts = ax.pie(
            status_counts.values,
            labels=status_counts.index,
            colors=colors,
            autopct=lambda pct: autopct_format(pct, status_counts.values),
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Proporción por Estado', fontweight='bold')
    
    def _subplot_status_trend_over_time(self, df: pd.DataFrame, ax) -> None:
        """Genera subplot de tendencia de estados."""
        df_grouped = df.groupby(['created_week', 'status']).size().unstack(fill_value=0)
        status_order = ['PENDIENTE', 'EN CURSO', 'FINALIZADA']
        df_grouped = df_grouped.reindex(columns=status_order, fill_value=0)
        
        x = range(len(df_grouped))
        colors = [self.STATUS_COLORS[s] for s in df_grouped.columns]
        
        ax.stackplot(x, 
                    [df_grouped[col].values for col in df_grouped.columns],
                    labels=df_grouped.columns,
                    colors=colors,
                    alpha=0.8)
        
        ax.set_title('Tendencia de Estados', fontweight='bold')
        ax.set_xlabel('Semana', fontweight='bold')
        ax.set_ylabel('Cantidad (Acumulado)', fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(axis='y', alpha=0.3)
