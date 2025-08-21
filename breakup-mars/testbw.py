import math

material_result = ""
diameter_result = 0
thickness_result = 1
area_result = 0
weight_result = 0

material_density = {
    "유리": 2.4,
    "알루미늄": 2.7,
    "탄소강": 7.85
}

def sphere_area(diameter, material="유리", thickness=1):
    global material_result, diameter_result, thickness_result, area_result, weight_result

    radius = diameter / 2
    area = 2 * math.pi * radius ** 2
    volume_cm3 = area * (thickness / 100) * 1_000_000

    density = material_density.get(material, material_density["유리"])
    mass_kg = (volume_cm3 * density) / 1000
    weight_kg = mass_kg * 0.38

    area = round(area, 3)
    weight_kg = round(weight_kg, 3)

    material_result = material
    diameter_result = diameter
    thickness_result = thickness
    area_result = area
    weight_result = weight_kg


while True:
    material = input("재질을 입력하세요 종료하려면 -1을 입력해주세요 (유리/알루미늄/탄소강): ").strip()
    if material not in material_density:
        if material=='-1':
            break
        print("잘못된 재질입니다. 유리, 알루미늄, 탄소강 중에서 선택해주세요.")
        continue
    try:
        diameter = float(input("지름을 입력하세요 (m): "))
        if diameter < 0:
            print("자연수 값을 입력해주세요.")
            continue
        sphere_area(diameter, material)
        print(f"재질 ⇒ {material_result}, 지름 ⇒ {diameter_result}, 두께 ⇒ {thickness_result}, 면적 ⇒ {area_result}, 무게 ⇒ {weight_result} kg")
    except ValueError:
        print("지름은 숫자 형식으로 입력해야 합니다.")
print('종료되었습니다')