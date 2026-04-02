import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service({ title: "Library API", version: "1.0.0" })
namespace LibraryAPI;

model Book {
  id: int32;
  title: string;
  author: string;
  available: boolean;
}

model Loan {
  id: int32;
  memberId: int32;
  bookId: int32;
  dueDate: plainDate;
  status: string;
}

@route("/books")
interface Books {
  @get list(): Book[];
  @post create(@body body: Book): Book;
  @get @route("/{id}") get(@path id: int32): Book;
}

@route("/loans")
interface Loans {
  @post create(@body body: Loan): Loan;
  @post @route("/{id}/return") returnBook(@path id: int32): Loan;
}
