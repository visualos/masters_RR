import os
import re
import shutil

# --- KONFIGURACJA ŚCIEŻEK ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_raw = os.path.join(base_dir, 'pliki_fotometryczne', '5_LUG', 'lug_razem')
path_s1 = os.path.join(base_dir, 'pliki_fotometryczne', '5_LUG', 'lug_razem_sorted')
path_s2 = os.path.join(base_dir, 'pliki_fotometryczne', '5_LUG', 'lug_razem_sorted_2')
path_s3 = os.path.join(base_dir, 'pliki_fotometryczne', '5_LUG', 'lug_razem_sorted_3')


def extract_key_v1(filename):
    """Klucz dla etapu 1: Podstawowe parametry techniczne."""
    pattern = r"([A-Z0-9]+_LED_\d+W_\d+lm_\d+K_IP\d+_O\d+)"
    match = re.search(pattern, filename)
    return match.group(1) if match else None


def extract_key_v2(filename):
    """Klucz dla etapu 2: Tylko nazwa i optyka (usuwanie kolorów/opisów)."""
    pattern = r"([A-Z0-9]+_LED.*_O\d+)"
    match = re.search(pattern, filename)
    return match.group(1) if match else None


def extract_key_v3(filename):
    """Klucz dla etapu 3: Ignorowanie DALI/ED (łączenie w pary sterowania)."""
    pattern = r"([A-Z0-9]+_LED)_(?:ED_|DALI_)?(\d+W_\d+lm_\d+K_IP\d+_O\d+)"
    match = re.search(pattern, filename)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return None


def process_stage(source, target, key_func, mode='unique', stage_name=""):
    """Uniwersalna funkcja do przetwarzania etapów."""
    print(f"\n>>> URUCHAMIAM ETAP {stage_name}")
    if not os.path.exists(source):
        print(f"Błąd: Brak folderu źródłowego {source}")
        return False
    if not os.path.exists(target):
        os.makedirs(target)

    files = sorted([f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))])

    if mode == 'unique':
        seen = {}
        for f in files:
            k = key_func(f)
            if k not in seen:
                shutil.copy2(os.path.join(source, f), os.path.join(target, f))
                seen[k] = f
        print(f"Zakończono: {len(seen)} plików w {target}")

    elif mode == 'dali_filter':
        groups = {}
        for f in files:
            k = key_func(f)
            if k:
                groups.setdefault(k, []).append(f)
            else:
                shutil.copy2(os.path.join(source, f), os.path.join(target, f))

        count = 0
        for k, f_list in groups.items():
            non_dali = [f for f in f_list if "DALI" not in f.upper()]
            chosen = sorted(non_dali)[0] if non_dali else sorted(f_list)[0]
            shutil.copy2(os.path.join(source, chosen), os.path.join(target, chosen))
            count += 1
        print(f"Zakończono: {count} plików w {target} (odfiltrowano DALI)")
    return True


def main():
    # ETAP 1: Podstawowe czyszczenie duplikatów
    if process_stage(path_raw, path_s1, extract_key_v1, 'unique', "1 (Podstawowy)"):

        # ETAP 2: Usuwanie wariantów kolorystycznych (Szary/Grafit itp.)
        if process_stage(path_s1, path_s2, extract_key_v2, 'unique', "2 (Kolory)"):
            # ETAP 3: Usuwanie DALI (jeśli istnieje odpowiednik bez DALI)
            process_stage(path_s2, path_s3, extract_key_v3, 'dali_filter', "3 (DALI vs ED)")

    print("\n" + "=" * 40)
    print("PROCES ZAKOŃCZONY POMYŚLNIE")
    print(f"Finalne pliki znajdziesz w: {path_s3}")


if __name__ == "__main__":
    main()