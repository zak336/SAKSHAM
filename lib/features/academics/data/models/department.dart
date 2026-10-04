import 'package:json_annotation/json_annotation.dart';

part 'department.g.dart';

@JsonSerializable()
class Department {
  const Department({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.code,
    required this.isActive,
  });

  final String id;

  @JsonKey(name: 'tenant_id')
  final String tenantId;

  final String name;
  final String code;

  @JsonKey(name: 'is_active')
  final bool isActive;

  factory Department.fromJson(Map<String, dynamic> json) =>
      _$DepartmentFromJson(json);

  Map<String, dynamic> toJson() => _$DepartmentToJson(this);
}
