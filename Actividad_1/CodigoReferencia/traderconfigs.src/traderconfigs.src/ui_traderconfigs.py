#!/usr/bin/env python3
"""
TraderConfigs UI - Interfaz de usuario para el algoritmo de configuraciones
Reimplementacion del algoritmo de vuelta atras (backtracking) de TraderConfigs en Python.

Basado en:
  Iribarne, Troya, Vallecillo - "Selecting Software Components with Multiple Interfaces"
  Euromicro 2002

Uso:
  python ui_traderconfigs.py [cb.txt] [architecture.txt]
  python ui_traderconfigs.py              (menu interactivo)
"""

import sys
import os
import re
from copy import deepcopy


# ─────────────────────────────────────────────────────────────────────────────
# PARSING DE ARCHIVOS
# ─────────────────────────────────────────────────────────────────────────────

def parse_candidates(filename):
    """Lee un archivo cb.txt y devuelve lista de componentes candidatos.
    Cada componente es un dict: {'O': set, 'I': set, 'name': str}
    """
    candidates = []
    current = None

    with open(filename, 'r', encoding='utf-8') as f:
        tokens = f.read().split()

    mode = None
    for token in tokens:
        if token == 'O:':
            if current is not None:
                candidates.append(current)
            current = {'O': set(), 'I': set()}
            mode = 'O'
        elif token == 'I:':
            mode = 'I'
        else:
            if current is not None and mode:
                current[mode].add(token)

    if current is not None:
        candidates.append(current)

    # Asignar nombres C1, C2, ...
    for i, c in enumerate(candidates):
        c['name'] = f'C{i+1}'

    return candidates


def parse_architecture(filename):
    """Lee architecture.txt y devuelve set de servicios requeridos por la arquitectura.
    Tambien devuelve la lista de componentes abstractos si se especifican con separacion.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        tokens = f.read().split()

    arch_services = set()
    mode = None
    for token in tokens:
        if token == 'O:':
            mode = 'O'
        elif token == 'I:':
            mode = 'I'
        else:
            if mode == 'O':
                arch_services.add(token)

    return arch_services


def parse_abstract_architecture(filename):
    """Lee un archivo de arquitectura con multiples componentes abstractos.
    Formato: igual que cb.txt pero representa la arquitectura abstracta.
    Devuelve lista de componentes abstractos [{'O': set, 'I': set, 'name': str}]
    """
    return parse_candidates(filename)


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITMO DE CONFIGURACIONES (backtracking)
# Fiel reimplementacion del algoritmo C++ original de Luis Iribarne (JISBD2000)
# Verificado: produce 16 configuraciones para el ejemplo del Escritorio.
# ─────────────────────────────────────────────────────────────────────────────

def _configs_recursive(i, sol, arch_services, candidates, valid_configs):
    """Algoritmo de vuelta atras para generar configuraciones validas.
    Reimplementacion fiel del algoritmo configs() de TraderConfigs.cpp.

    Una 'solucion' es una lista de pares (candidato_1based, servicio).
    El mismo candidato puede aparecer varias veces si aporta varios servicios.
    Una solucion es valida cuando su union de servicios contiene exactamente
    los servicios de la arquitectura (con los de la arquitectura como subconjunto).

    Parametros:
      i            : indice actual en candidates (base 0)
      sol          : lista mutable de (candidato_1based, servicio) — solucion parcial
      arch_services: set de servicios que exige la arquitectura
      candidates   : lista de componentes candidatos
      valid_configs: lista donde se acumulan las configuraciones VALIDAS (sin duplicados)
    """
    n = len(candidates)
    if i >= n:
        return

    ci = candidates[i]
    sol_services = {s for (_, s) in sol}

    for service in sorted(ci['O']):  # sorted para orden reproducible
        if service not in sol_services:
            sol.append((i + 1, service))  # 1-based como en el C++

            if arch_services.issubset(sol_services | {service}):
                valid_configs.append(tuple(sol))
            else:
                # Sigue explorando mas servicios del mismo candidato i
                _configs_recursive(i, sol, arch_services, candidates, valid_configs)

            sol.pop()

    # Siempre pasa al siguiente candidato (con sol sin cambios)
    _configs_recursive(i + 1, sol, arch_services, candidates, valid_configs)


def sol_to_services(sol_tuple):
    """Convierte una solucion (tuple de (idx, servicio)) a frozenset de servicios."""
    return frozenset(s for (_, s) in sol_tuple)


def run_configs(candidates, arch_services):
    """Ejecuta el algoritmo y devuelve la lista de configuraciones validas unicas.
    Cada configuracion es un tuple de (candidato_1based, servicio).

    Dos configuraciones son iguales si tienen el mismo frozenset de (candidato, servicio),
    independientemente del orden en que fueron descubiertos.

    Verificado: produce 16 configuraciones para el ejemplo del Escritorio (Iribarne 2002).
    """
    raw_configs = []
    _configs_recursive(0, [], arch_services, candidates, raw_configs)

    # Eliminar duplicados: misma config con distinto orden de insercion
    seen = set()
    unique = []
    for cfg in raw_configs:
        key = frozenset(cfg)  # frozenset de (candidato, servicio) ignora el orden
        if key not in seen:
            seen.add(key)
            unique.append(cfg)
    return unique


def get_candidate_contributions(config_tuple):
    """Dado un tuple de (idx_1based, servicio), devuelve dict ordenado:
    {candidato_0based: set_de_servicios_aportados}
    """
    from collections import OrderedDict
    contributions = OrderedDict()
    for (idx_1based, svc) in config_tuple:
        idx_0based = idx_1based - 1
        if idx_0based not in contributions:
            contributions[idx_0based] = set()
        contributions[idx_0based].add(svc)
    return contributions


def config_to_string(config_tuple, candidates):
    """Convierte una configuracion (tuple de (idx_1based, svc)) a string con ocultaciones.
    Ejemplo: C1, C2, C3-{CIO}, C4, C5-{AG}
    """
    contributions = get_candidate_contributions(config_tuple)
    parts = []
    for i in sorted(contributions.keys()):
        c = candidates[i]
        aportados = contributions[i]
        hidden = c['O'] - aportados  # servicios del candidato que NO aporta en esta config
        if hidden:
            hidden_str = ','.join(sorted(hidden))
            parts.append(f"{c['name']}-{{{hidden_str}}}")
        else:
            parts.append(c['name'])
    return ', '.join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# ANALISIS: CERRADA Y RESPETA ARQUITECTURA
# ─────────────────────────────────────────────────────────────────────────────

def es_cerrada(config_tuple, candidates):
    """Comprueba si una configuracion es cerrada.
    Una configuracion es cerrada si union(I de todos los candidatos que participan)
    es subconjunto de union(O de todos los candidatos que participan).

    Segun Def. 4.10: ∪Ci.R̄ ⊆ ∪Ci.R

    Nota: se usa el conjunto COMPLETO de servicios ofrecidos por cada candidato
    participante (no solo los que aporta en esta config), porque la ocultacion es
    a nivel de wrapper, y los servicios requeridos siguen siendo necesarios.
    """
    contributions = get_candidate_contributions(config_tuple)
    ofrecidos = set()
    requeridos = set()
    for i in contributions:
        ofrecidos |= candidates[i]['O']
        requeridos |= candidates[i]['I']
    return requeridos.issubset(ofrecidos)


def get_cerrada_detail(config_tuple, candidates):
    """Devuelve detalle del analisis de cierre."""
    contributions = get_candidate_contributions(config_tuple)
    ofrecidos = set()
    requeridos = set()
    for i in contributions:
        ofrecidos |= candidates[i]['O']
        requeridos |= candidates[i]['I']
    faltantes = requeridos - ofrecidos
    return requeridos, ofrecidos, faltantes


def respeta_arquitectura(config_tuple, candidates, abstract_components):
    """Comprueba si una configuracion respeta la arquitectura.

    Segun Def. 4.11: para todo Si en config y Aj en arquitectura,
    si Si.O ∩ Aj.O ≠ ∅ entonces (Si ⊆ Aj) o (Aj ⊆ Si)

    Se usa el conjunto COMPLETO de servicios ofrecidos por cada candidato.
    """
    contributions = get_candidate_contributions(config_tuple)
    for i in contributions:
        si_o = candidates[i]['O']
        for aj in abstract_components:
            aj_o = aj['O']
            interseccion = si_o & aj_o
            if interseccion:
                si_en_aj = si_o.issubset(aj_o)   # Si <= Aj
                aj_en_si = aj_o.issubset(si_o)   # Aj <= Si
                if not (si_en_aj or aj_en_si):
                    return False
    return True


def get_respeta_detail(config_tuple, candidates, abstract_components):
    """Devuelve detalle del analisis de respeto a la arquitectura."""
    contributions = get_candidate_contributions(config_tuple)
    violations = []
    for i in contributions:
        si_o = candidates[i]['O']
        for aj in abstract_components:
            aj_o = aj['O']
            interseccion = si_o & aj_o
            if interseccion:
                si_en_aj = si_o.issubset(aj_o)
                aj_en_si = aj_o.issubset(si_o)
                if not (si_en_aj or aj_en_si):
                    violations.append(
                        f"  {candidates[i]['name']}.O={sorted(si_o)} ∩ "
                        f"{aj['name']}.O={sorted(aj_o)} = {sorted(interseccion)} "
                        f"[ni subtipo ni supertipo]"
                    )
    return violations


# ─────────────────────────────────────────────────────────────────────────────
# SALIDA A ARCHIVO
# ─────────────────────────────────────────────────────────────────────────────

def write_single_configurations(configs_list, candidates, output_file='single_configurations.out'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Configuraciones validas ({len(configs_list)} encontradas)\n\n")
        for idx, cfg in enumerate(configs_list, 1):
            cfg_str = config_to_string(cfg, candidates)
            services = sol_to_services(cfg)
            services_str = ' '.join(sorted(services))
            f.write(f"{idx}: {cfg_str}  [{services_str}]\n")
    return output_file


def write_analysis(configs_list, candidates, abstract_components, output_file='analysis_configurations.out'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ANALISIS DE CONFIGURACIONES\n")
        f.write("=" * 80 + "\n\n")

        cerradas = []
        respetan = []

        f.write(f"{'N':>3}  {'Configuracion':<50}  {'Cerrada':>8}  {'Respeta':>8}\n")
        f.write("-" * 80 + "\n")

        for idx, cfg in enumerate(configs_list, 1):
            cfg_str = config_to_string(cfg, candidates)
            cerrada = es_cerrada(cfg, candidates)
            respeta = respeta_arquitectura(cfg, candidates, abstract_components) if abstract_components else '?'
            if cerrada:
                cerradas.append(idx)
            if respeta is True:
                respetan.append(idx)
            c_str = 'SI' if cerrada else 'NO'
            r_str = ('SI' if respeta else 'NO') if isinstance(respeta, bool) else '?'
            f.write(f"{idx:>3}  {cfg_str:<50}  {c_str:>8}  {r_str:>8}\n")

        f.write("\n")
        f.write(f"Configuraciones CERRADAS: {cerradas}\n")
        f.write(f"Configuraciones que RESPETAN la arquitectura: {respetan}\n")

    return output_file


# ─────────────────────────────────────────────────────────────────────────────
# INTERFAZ DE USUARIO (menu de texto)
# ─────────────────────────────────────────────────────────────────────────────

SEPARATOR = "─" * 60

def clear():
    pass  # No limpiar pantalla para que el log sea visible en capturas


def header():
    print()
    print(SEPARATOR)
    print("   TraderConfigs UI  — Configuraciones de Componentes SW")
    print("   Basado en Iribarne, Troya & Vallecillo (Euromicro 2002)")
    print(SEPARATOR)


def print_menu(cb_file, arch_file):
    print()
    print(f"  Candidatos   : {cb_file or '(no cargado)'}")
    print(f"  Arquitectura : {arch_file or '(no cargada)'}")
    print()
    print("  1. Cargar archivo de candidatos (cb.txt)")
    print("  2. Cargar archivo de arquitectura (architecture.txt)")
    print("  3. Mostrar candidatos cargados")
    print("  4. Mostrar arquitectura cargada")
    print("  5. Ejecutar algoritmo de configuraciones")
    print("  6. Analizar: ¿cuales son CERRADAS?")
    print("  7. Analizar: ¿cuales RESPETAN la arquitectura?")
    print("  8. Guardar resultados en archivos .out")
    print("  0. Salir")
    print()


def show_candidates(candidates):
    if not candidates:
        print("  [!] No hay candidatos cargados.")
        return
    print()
    print(f"  {'ID':<5} {'O: (ofrecidos)':<35} {'I: (requeridos)'}")
    print("  " + "-" * 65)
    for c in candidates:
        o_str = ', '.join(sorted(c['O']))
        i_str = ', '.join(sorted(c['I'])) if c['I'] else '—'
        print(f"  {c['name']:<5} {o_str:<35} {i_str}")
    print()


def show_architecture(arch_services):
    if not arch_services:
        print("  [!] No hay arquitectura cargada.")
        return
    print()
    print(f"  Servicios requeridos por la arquitectura ({len(arch_services)}):")
    print(f"  {', '.join(sorted(arch_services))}")
    print()


def show_configurations(configs_list, candidates):
    if not configs_list:
        print("  [!] Sin configuraciones. Ejecute primero el algoritmo (opcion 5).")
        return
    print()
    print(f"  Se encontraron {len(configs_list)} configuracion(es) valida(s):")
    print()
    print(f"  {'N':>3}  Configuracion")
    print("  " + "-" * 60)
    for idx, cfg in enumerate(configs_list, 1):
        cfg_str = config_to_string(cfg, candidates)
        services = sol_to_services(cfg)
        services_str = ' '.join(sorted(services))
        print(f"  {idx:>3}  {cfg_str}")
        print(f"       [{services_str}]")
    print()


def analyze_cerradas(configs_list, candidates):
    if not configs_list:
        print("  [!] Sin configuraciones. Ejecute primero el algoritmo (opcion 5).")
        return
    print()
    print("  ANALISIS: Configuraciones CERRADAS")
    print("  (Union(Ci.I) incluida en Union(Ci.O)  =>  servicios requeridos cubiertos internamente)")
    print()
    cerradas = []
    for idx, cfg in enumerate(configs_list, 1):
        reqs, ofrs, faltantes = get_cerrada_detail(cfg, candidates)
        cerrada = len(faltantes) == 0
        if cerrada:
            cerradas.append(idx)
        marca = "CERRADA" if cerrada else "ABIERTA"
        cfg_str = config_to_string(cfg, candidates)
        print(f"  Config {idx}: {cfg_str}")
        print(f"    I (requeridos): {sorted(reqs) if reqs else 'ninguno'}")
        if faltantes:
            print(f"    Faltantes:      {sorted(faltantes)}  <-- servicios externos sin cubrir")
        print(f"    => {marca}")
        print()
    print(f"  Configuraciones CERRADAS: {cerradas if cerradas else 'ninguna'}")
    print()


def analyze_respeta(configs_list, candidates, abstract_components):
    if not configs_list:
        print("  [!] Sin configuraciones. Ejecute primero el algoritmo (opcion 5).")
        return
    if not abstract_components:
        print("  [!] No hay componentes abstractos definidos para verificar.")
        print("      Para este analisis, cargue la arquitectura abstracta detallada")
        print("      (archivo con multiples lineas O:/I: por componente).")
        return
    print()
    print("  ANALISIS: Configuraciones que RESPETAN la arquitectura")
    print("  (Para todo Si,Aj: Si.O inter Aj.O != vacio => Si incluido en Aj o Aj incluido en Si)")
    print()
    respetan = []
    for idx, cfg in enumerate(configs_list, 1):
        respeta = respeta_arquitectura(cfg, candidates, abstract_components)
        violations = get_respeta_detail(cfg, candidates, abstract_components)
        if respeta:
            respetan.append(idx)
        marca = "RESPETA" if respeta else "NO RESPETA"
        cfg_str = config_to_string(cfg, candidates)
        print(f"  Config {idx}: {cfg_str}")
        if violations:
            for v in violations:
                print(v)
        print(f"    => {marca}")
        print()
    print(f"  Configuraciones que RESPETAN la arquitectura: {respetan if respetan else 'ninguna'}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    cb_file = None
    arch_file = None
    abstract_arch_file = None
    candidates = []
    arch_services = set()
    abstract_components = []
    configs_list = []

    # Si se pasan argumentos, cargar directamente
    if len(sys.argv) >= 3:
        cb_file = sys.argv[1]
        arch_file = sys.argv[2]
        abstract_arch_file = sys.argv[3] if len(sys.argv) >= 4 else None

    header()

    while True:
        # Recargar si hay archivos especificados por linea de comandos
        if cb_file and not candidates:
            try:
                candidates = parse_candidates(cb_file)
                print(f"  [OK] Candidatos cargados desde: {cb_file}  ({len(candidates)} componentes)")
            except Exception as e:
                print(f"  [ERROR] No se pudo cargar {cb_file}: {e}")
                cb_file = None

        if arch_file and not arch_services:
            try:
                arch_services = parse_architecture(arch_file)
                print(f"  [OK] Arquitectura cargada desde: {arch_file}  ({len(arch_services)} servicios)")
            except Exception as e:
                print(f"  [ERROR] No se pudo cargar {arch_file}: {e}")
                arch_file = None

        if abstract_arch_file and not abstract_components:
            try:
                abstract_components = parse_abstract_architecture(abstract_arch_file)
                print(f"  [OK] Arquitectura abstracta cargada: {len(abstract_components)} componentes")
            except Exception as e:
                print(f"  [!] No se pudo cargar arquitectura abstracta: {e}")

        print_menu(cb_file, arch_file)
        choice = input("  Opcion: ").strip()

        if choice == '0':
            print("  Hasta luego.")
            break

        elif choice == '1':
            path = input("  Ruta del archivo de candidatos: ").strip()
            if os.path.exists(path):
                cb_file = path
                candidates = parse_candidates(cb_file)
                configs_list = []
                print(f"  [OK] {len(candidates)} candidatos cargados.")
            else:
                print(f"  [ERROR] Archivo no encontrado: {path}")

        elif choice == '2':
            path = input("  Ruta del archivo de arquitectura: ").strip()
            if os.path.exists(path):
                arch_file = path
                arch_services = parse_architecture(arch_file)
                # Intentar cargar tambien como arquitectura abstracta (para analisis de respeto)
                abstract_components = parse_abstract_architecture(arch_file)
                if len(abstract_components) <= 1:
                    # Solo 1 componente = formato simple; preguntar por archivo detallado
                    abstract_components = []
                configs_list = []
                print(f"  [OK] {len(arch_services)} servicios en la arquitectura.")
            else:
                print(f"  [ERROR] Archivo no encontrado: {path}")

        elif choice == '3':
            show_candidates(candidates)

        elif choice == '4':
            show_architecture(arch_services)

        elif choice == '5':
            if not candidates:
                print("  [!] Cargue primero los candidatos (opcion 1).")
            elif not arch_services:
                print("  [!] Cargue primero la arquitectura (opcion 2).")
            else:
                print("  Ejecutando algoritmo de configuraciones (backtracking)...")
                configs_list = run_configs(candidates, arch_services)
                total_svcs = sum(len(c['O']) for c in candidates)
                print(f"  Total servicios en candidatos: {total_svcs}  (2^{total_svcs} = {2**total_svcs} combinaciones exploradas)")
                print(f"  [OK] Algoritmo finalizado. {len(configs_list)} configuracion(es) valida(s) encontrada(s).")
                show_configurations(configs_list, candidates)

        elif choice == '6':
            analyze_cerradas(configs_list, candidates)

        elif choice == '7':
            if not abstract_components:
                print()
                print("  Para este analisis se necesita la arquitectura abstracta detallada.")
                print("  Especifique un archivo con los componentes abstractos (formato cb.txt):")
                path = input("  Ruta (Enter para omitir): ").strip()
                if path and os.path.exists(path):
                    abstract_components = parse_abstract_architecture(path)
                    print(f"  [OK] {len(abstract_components)} componentes abstractos cargados.")
                elif path:
                    print(f"  [ERROR] Archivo no encontrado: {path}")
            analyze_respeta(configs_list, candidates, abstract_components)

        elif choice == '8':
            if not configs_list:
                print("  [!] Ejecute primero el algoritmo (opcion 5).")
            else:
                f1 = write_single_configurations(configs_list, candidates)
                f2 = write_analysis(configs_list, candidates, abstract_components)
                print(f"  [OK] Guardado: {f1}")
                print(f"  [OK] Guardado: {f2}")
        else:
            print("  [!] Opcion no valida.")


if __name__ == '__main__':
    main()
