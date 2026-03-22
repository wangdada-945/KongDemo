/**
 * Fast smoke: validates Kong is up via Admin API (no UI).
 * Good for CI stability and "layered testing" story in interviews.
 */
describe("Kong Admin API smoke", () => {
  const adminUrl = Cypress.env("KONG_ADMIN_URL") || "http://localhost:8001";

  it("Admin API root responds 200", () => {
    cy.request({ url: `${adminUrl}/`, failOnStatusCode: false }).then((res) => {
      expect(res.status, "Kong Admin API should be reachable").to.eq(200);
    });
  });
});
