# So sánh các Format Tài liệu hóa API

So sánh 4 format tài liệu hóa API phổ biến và demo với ứng dụng quản lý thư viện.

## Bảng so sánh

| Tiêu chí | OpenAPI | API Blueprint | RAML | TypeSpec |
|---|---|---|---|---|
| **Cú pháp** | YAML hoặc JSON | Markdown | YAML | TypeScript-like (DSL) |
| **Ưu điểm chính**| Cộng đồng khổng lồ, tool xịn | Gần gũi, đọc như văn bản thường | Tái sử dụng code cực kỳ tốt | Tựa code thật, bắt lỗi (type-check) |
| **Nhược điểm** | File cấu hình khá dài dòng | Ít công cụ hỗ trợ nâng cao | Hơi kén người dùng, độ phổ biến thấp | Mới quá, còn ít ví dụ thực tế |
| **Demo trong bài**| `0_OpenAPI/api.yaml` | `1_APIBlueprint/api.apib` | `2_RAML/api.raml` | `3_TypeSpec/main.tsp` |
| **Sinh code/Test**| Rất mạnh (xem `code-generation`) | Hạn chế (chủ yếu test Dredd) | Ở mức độ khá | Thường compile ngược ra OpenAPI |

### Nhận xét chung
- **OpenAPI**: Hệ sinh thái mạnh nhất (sinh code, UI) nhưng file dễ bị cồng kềnh, khó quản lý khi dự án lớn.
- **API Blueprint**: Cực kỳ dễ đọc và thân thiện với con người nhưng khả năng tự động hóa (tooling) yếu.
- **RAML**: Tổ chức code và tái sử dụng xuất sắc nhưng cộng đồng đang thu hẹp, chủ yếu xoay quanh MuleSoft.
- **TypeSpec**: Viết giống code thật, gọn nhẹ hơn OpenAPI nhưng còn quá mới, ít tài liệu và ví dụ thực tế.
