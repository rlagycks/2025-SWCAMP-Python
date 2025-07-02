import math

# 전역 변수 선언
material_result = ""
diameter_result = 0
thickness_result = 1
area_result = 0
weight_result = 0

# 재질별 밀도 (g/cm³)
material_density = {
    "유리": 2.4,
    "알루미늄": 2.7,
    "탄소강": 7.85
}

def sphere_area(diameter, material="유리", thickness=1):
    global material_result, diameter_result, thickness_result, area_result, weight_result

    radius = diameter / 2  # 지름에서 반지름
    area = 2 * math.pi * radius ** 2  # 반구의 겉면적 (m^2)

    # 면적을 이용해 두께만큼의 부피 계산 (단위 맞추기: m^2 × cm → cm³)
    volume_cm3 = area * (thickness / 100) * 1_000_000  # m² * m = m³ = 1e6 cm³

    # 밀도 가져오기 (기본은 유리)
    density = material_density.get(material, material_density["유리"])

    # 질량 (g 단위) → kg 단위
    mass_kg = (volume_cm3 * density) / 1000

    # 화성 중력 적용 (지구의 0.38배)
    weight_kg = mass_kg * 0.38

    # 소수점 셋째 자리까지 반올림
    area = round(area, 3)
    weight_kg = round(weight_kg, 3)

    # 전역 변수 저장
    material_result = material
    diameter_result = diameter
    thickness_result = thickness
    area_result = area
    weight_result = weight_kg

    # 출력
    print(f"재질 ⇒ {material_result}, 지름 ⇒ {diameter_result}, 두께 ⇒ {thickness_result}, 면적 ⇒ {area_result}, 무게 ⇒ {weight_result} kg")

# 사용자 입력
material = input("재질을 입력하세요 (유리/알루미늄/탄소강): ").strip()
diameter = float(input("지름을 입력하세요 (m): "))

# 함수 호출
sphere_area(diameter, material)