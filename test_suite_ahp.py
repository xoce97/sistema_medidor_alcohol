#!/usr/bin/env python3
"""
Test Suite Completo - Sistema AHP
Valida todas las funcionalidades del dashboard AHP
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alcoholimetro2025.settings')
django.setup()

from django.test import Client
from medidor.models import Empleado, MuestraAlcohol
from medidor.analisis_ahp import AnalizadorAHP
import json

class TestSuiteAHP:
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        
    def test_login(self):
        """Test autenticación del admin"""
        print("\n[TEST 1] Autenticación")
        if not Empleado.objects.filter(username='admin').exists():
            Empleado.objects.create_superuser(
                username='admin', email='admin@test.com', password='admin123',
                identificacion='0000', first_name='Admin', last_name='User'
            )
        
        ok = self.client.login(username='admin', password='admin123')
        self._assert(ok, "Login exitoso")
        
    def test_dashboard_general(self):
        """Test dashboard sin filtros"""
        print("\n[TEST 2] Dashboard General")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        self._assert(b'Chart.js' in response.content, "Chart.js presente")
        self._assert(b'AHP' in response.content, "Contenido AHP presente")
        
    def test_dashboard_departamento_filter(self):
        """Test dashboard con filtro de departamento"""
        print("\n[TEST 3] Filtro por Departamento")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/?departamento=Ventas')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        self._assert(b'Ventas' in response.content, "Departamento en respuesta")
        
    def test_dashboard_date_filter(self):
        """Test dashboard con filtro de fechas"""
        print("\n[TEST 4] Filtro por Rango de Fechas")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/?fecha_inicio=2025-01-01&fecha_fin=2025-12-31')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        
    def test_dashboard_low_risk(self):
        """Test dashboard ordenado por bajo riesgo"""
        print("\n[TEST 5] Orden Bajo Riesgo")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/?orden=menor')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        
    def test_export_pdf(self):
        """Test exportación a PDF"""
        print("\n[TEST 6] Export PDF")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/export-pdf/?departamento=None&fecha_inicio=None&fecha_fin=None&orden=mayor')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        self._assert('application/pdf' in response.get('Content-Type', ''), f"Content-Type PDF (got {response.get('Content-Type')})")
        self._assert(len(response.content) > 1000, f"PDF size > 1000 bytes (got {len(response.content)})")
        
    def test_export_csv(self):
        """Test exportación a CSV"""
        print("\n[TEST 7] Export CSV")
        response = self.client.get('/admin/medidor/empleado/dashboard-ahp/export-csv/?departamento=None&fecha_inicio=None&fecha_fin=None&orden=mayor')
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        self._assert('text/csv' in response.get('Content-Type', ''), f"Content-Type CSV (got {response.get('Content-Type')})")
        csv_content = response.content.decode('utf-8')
        self._assert('Identificaci' in csv_content, "Headers presentes en CSV")
        self._assert(len(response.content) > 500, f"CSV size > 500 bytes (got {len(response.content)})")
        
    def test_ahp_engine(self):
        """Test motor AHP directamente"""
        print("\n[TEST 8] Motor AHP")
        ahp = AnalizadorAHP()
        df = ahp.analizar(limite=10)
        self._assert(len(df) > 0, f"Datos retornados (got {len(df)})")
        self._assert('ahp_score' in df.columns, "Columna ahp_score presente")
        self._assert('nivel_riesgo' in df.columns, "Columna nivel_riesgo presente")
        self._assert((df['ahp_score'] >= 0).all() and (df['ahp_score'] <= 100).all(), "Scores en rango 0-100")
        
    def test_ahp_filter_departamento(self):
        """Test AHP con filtro de departamento"""
        print("\n[TEST 9] AHP + Filtro Departamento")
        ahp = AnalizadorAHP()
        df = ahp.analizar(departamento='Ventas', limite=10)
        if len(df) > 0:
            self._assert((df['departamento'] == 'Ventas').all(), "Todos son del departamento Ventas")
        else:
            self._assert(True, "Sin datos (es válido)")
            
    def test_ahp_low_risk_ordering(self):
        """Test AHP ordenado por bajo riesgo"""
        print("\n[TEST 10] AHP + Orden Bajo Riesgo")
        ahp = AnalizadorAHP()
        df = ahp.analizar(limite=10, ordenar_descendente=False)
        self._assert(len(df) > 0, "Datos retornados")
        if len(df) > 1:
            # Verificar que está ordenado ascendente (bajo riesgo primero)
            is_ascending = (df['ahp_score'].iloc[0] <= df['ahp_score'].iloc[-1])
            self._assert(is_ascending, "Ordenamiento ascendente (bajo riesgo primero)")
            
    def test_database_stats(self):
        """Test estadísticas de base de datos"""
        print("\n[TEST 11] Estadísticas de Base de Datos")
        emp_count = Empleado.objects.count()
        samples_count = MuestraAlcohol.objects.count()
        
        self._assert(emp_count > 0, f"Empleados > 0 (got {emp_count})")
        self._assert(samples_count > 0, f"Muestras > 0 (got {samples_count})")
        self._assert(emp_count >= 50, f"Al menos 50 empleados (got {emp_count})")
        self._assert(samples_count >= 500, f"Al menos 500 muestras (got {samples_count})")
        
    def test_export_with_filters(self):
        """Test exportación con filtros combinados"""
        print("\n[TEST 12] Export PDF + Filtros")
        url = '/admin/medidor/empleado/dashboard-ahp/export-pdf/?departamento=Ventas&fecha_inicio=2025-01-01&fecha_fin=2025-12-31&orden=mayor'
        response = self.client.get(url)
        self._assert(response.status_code == 200, f"Status 200 (got {response.status_code})")
        self._assert('application/pdf' in response.get('Content-Type', ''), "Content-Type PDF")
        
    def _assert(self, condition, message):
        """Helper para assertions"""
        if condition:
            print(f"  ✓ {message}")
            self.passed += 1
        else:
            print(f"  ✗ {message}")
            self.failed += 1
            
    def run_all(self):
        """Ejecuta todas las pruebas"""
        print("\n" + "="*70)
        print("SUITE DE TESTS - SISTEMA AHP DE RIESGO DE ALCOHOL")
        print("="*70)
        
        try:
            self.test_login()
            self.test_database_stats()
            self.test_dashboard_general()
            self.test_dashboard_departamento_filter()
            self.test_dashboard_date_filter()
            self.test_dashboard_low_risk()
            self.test_export_pdf()
            self.test_export_csv()
            self.test_ahp_engine()
            self.test_ahp_filter_departamento()
            self.test_ahp_low_risk_ordering()
            self.test_export_with_filters()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.failed += 1
            
        # Resumen
        print("\n" + "="*70)
        print(f"RESULTADOS: {self.passed} PASSED, {self.failed} FAILED")
        print("="*70)
        
        if self.failed == 0:
            print("STATUS: ✓ COMPLETAMENTE OPERACIONAL")
            return 0
        else:
            print("STATUS: ✗ REVISAR ERRORES")
            return 1

if __name__ == '__main__':
    suite = TestSuiteAHP()
    sys.exit(suite.run_all())
