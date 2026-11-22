'use client';

import { apiFetch } from "@/lib/api";

import React, { useEffect, useState } from "react";
import { Plus, X, Pencil, Trash2 } from "lucide-react";

interface RowData extends Record<string, any> {}
interface FormData extends Record<string, any> {}

const sections: Record<string, string> = {
  "Users": "/categories/users",
  "Currencies": "/categories/currencies",
  "Regions": "/categories/region",
  "Income Sources": "/categories/income-sources",
  "Expense Categories": "/categories/expense-category",
  "Investment Categories": "/categories/investment-category",
  "Investment Subcategories": "/categories/investment-subcategory",
  "Units": "/categories/units",
};

const fieldMappings: Record<string, string[]> = {
  "Users": ["name"],
  "Currencies": ["currency_name", "currency_code"],
  "Regions": ["region_name", "currency_name"],
  "Income Sources": ["name", "description"],
  "Expense Categories": ["name", "description"],
  "Investment Categories": ["investment_type"],
  "Investment Subcategories": ["category_name", "investment_subcategory_name"],
  "Units": ["unit_name"],
};

const idKeyMappings: Record<string, string> = {
  "Users": "user_id",
  "Currencies": "currency_id",
  "Regions": "region_id",
  "Income Sources": "income_source_id",
  "Expense Categories": "expense_category_id",
  "Investment Categories": "id",
  "Investment Subcategories": "id",
  "Units": "unit_id",
};

export default function SupportingData() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormData>({});
  const [data, setData] = useState<Record<string, RowData[]>>({});
  const [activeSection, setActiveSection] = useState(Object.keys(sections)[0]);
  const [editingRow, setEditingRow] = useState<RowData | null>(null);
  const [investmentCategories, setInvestmentCategories] = useState<RowData[]>([]);
  const [currencies, setCurrencies] = useState<RowData[]>([]);

  const fetchCategories = async () => {
    try {
      const res = await apiFetch("/api/categories/investment-category");
      if (!res.ok) throw new Error("Failed to fetch categories");
      const json = await res.json();
      setInvestmentCategories(json);
      return json;
    } catch (error) {
      console.error("Error fetching categories:", error);
      return [];
    }
  };

const fetchCurrencies = async () => {
  try {
    const res = await apiFetch("/api/categories/currencies");
    if (!res.ok) throw new Error("Failed to fetch currencies");
    const json = await res.json();
    setCurrencies(json);
    return json;
  } catch (error) {
    console.error("Error fetching currencies:", error);
    return [];
  }
};

  const fetchData = async (section: string) => {
    try {
      const res = await apiFetch(`/api${sections[section]}`);
      if (!res.ok) throw new Error(`Failed to fetch ${section}`);
      let json: RowData[] = await res.json();

      if (section === "Investment Subcategories") {
        const cats = investmentCategories.length > 0 ? investmentCategories : await fetchCategories();
        json = json.map((sub: any) => ({
          ...sub,
          category_name: cats.find((c: any) => c.id === sub.category_id)?.investment_type || "N/A",  // Use c.id
        }));
      }

      if (section === "Regions") {
          const curs = currencies.length > 0 ? currencies : await fetchCurrencies();
          json = json.map((region: any) => ({
            ...region,
            currency_name: curs.find((c: any) => c.currency_id === region.currency_id)?.currency_name || "N/A",
          }));
      }

      setData((prev) => ({ ...prev, [section]: json }));
    } catch (error) {
      console.error(`Error fetching ${section}:`, error);
      setData((prev) => ({ ...prev, [section]: [] }));
    }
  };

  useEffect(() => {
  if (activeSection === "Investment Subcategories") {
        fetchCategories().then(() => fetchData(activeSection));
      } else if (activeSection === "Regions") {
        fetchCurrencies().then(() => fetchData(activeSection));
      } else {
        fetchData(activeSection);
      }
  }, [activeSection]);

  const handleDelete = async (section: string, id: number | undefined) => {  // Fixed type
    if (!id) return alert("Invalid item ID. Unable to delete.");
    if (!confirm("Are you sure you want to delete this item?")) return;

    try {
      const res = await apiFetch(`/api${sections[section]}/${id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        fetchData(section);
      } else {
        alert("Failed to delete item.");
      }
    } catch (error) {
      console.error("Error deleting item:", error);
      alert("An error occurred while deleting.");
    }
  };

  const handleSubmit = async () => {
    const idKey = idKeyMappings[activeSection];
    const url = editingRow
      ? `/api${sections[activeSection]}/${editingRow[idKey]}`
      : `/api${sections[activeSection]}`;

    try {
      const res = await fetch(url, {
        method: editingRow ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        setShowForm(false);
        setFormData({});
        setEditingRow(null);
        fetchData(activeSection);
      } else {
        alert("Failed to save item.");
      }
    } catch (error) {
      console.error("Error saving item:", error);
      alert("An error occurred while saving.");
    }
  };

  const handleEdit = (row: RowData) => {
    setEditingRow(row);
    const initialFormData: FormData = { ...row };

    if (activeSection === "Investment Subcategories") {
      const category = investmentCategories.find((c) => c.investment_type === row.category_name);
      if (category) {
        initialFormData.category_id = category.id;  // Use category.id
      }
    }

    if (activeSection === "Regions") {
      const currency = currencies.find((c) => c.currency_name === row.currency_name);
      if (currency) {
        initialFormData.currency_id = currency.currency_id;
      }
    }

    setFormData(initialFormData);
    setShowForm(true);
  };

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <h1 className="page-title">Master data configuration</h1>
          <p className="page-sub">
            The reference lists every transaction, portfolio and region points at.
          </p>
        </div>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingRow(null);
            setFormData({});
          }}
          className="btn btn-primary"
        >
          <Plus size={15} aria-hidden="true" />
          Add record
        </button>
      </div>

      <div className="seg" role="tablist" aria-label="Master data section">
        {Object.keys(sections).map((s) => (
          <button
            key={s}
            role="tab"
            aria-selected={activeSection === s}
            onClick={() => setActiveSection(s)}
            className={`seg-item ${activeSection === s ? "is-active" : ""}`}
          >
            {s}
          </button>
        ))}
      </div>

      <section className="card overflow-hidden">
        <div className="card-head">
          <h2 className="card-title">{activeSection}</h2>
          <span className="card-note">{data[activeSection]?.length || 0} records</span>
        </div>

        <div className="overflow-x-auto px-2 sm:px-3">
          {data[activeSection]?.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  {fieldMappings[activeSection]?.map((field) => (
                    <th key={field}>
                      {field.replace(/_/g, " ")}
                    </th>
                  ))}
                  <th className="num">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data[activeSection].map((row, idx) => {
                  const idKey = idKeyMappings[activeSection];
                  const rowId = row[idKey];
                  return (
                    <tr key={rowId || idx}>
                      {fieldMappings[activeSection]?.map((field) => (
                        <td key={field}>
                          {row[field] || <span className="text-[var(--color-muted)]">Not set</span>}
                        </td>
                      ))}
                      <td className="num">
                        <span className="inline-flex items-center gap-2">
                          <button
                            onClick={() => handleEdit(row)}
                            className="btn btn-secondary btn-sm"
                          >
                            <Pencil size={12} aria-hidden="true" />
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(activeSection, rowId)}
                            className="btn btn-danger btn-sm"
                          >
                            <Trash2 size={12} aria-hidden="true" />
                            Delete
                          </button>
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p className="state-title">No records found</p>
              <p className="text-[length:var(--text-sm)]">Add the first {activeSection.toLowerCase()} record to start using it.</p>
            </div>
          )}
        </div>
      </section>

      {showForm && (
          <div className="fixed inset-0 z-[400] flex items-start justify-center overflow-y-auto bg-[color-mix(in_oklab,var(--color-ink)_55%,transparent)] p-4 backdrop-blur-[2px] sm:items-center">
            <div className="card relative my-8 w-full max-w-[440px] p-6">
              <button
                onClick={() => {
                  setShowForm(false);
                  setFormData({});
                  setEditingRow(null);
                }}
                className="btn btn-ghost btn-icon btn-sm absolute right-4 top-4"
                aria-label="Close form"
              >
                <X size={16} aria-hidden="true" />
              </button>

              <h3 className="section-title mb-5 pr-10">
                {editingRow ? `Edit ${activeSection}` : `Add new ${activeSection}`}
              </h3>

              {fieldMappings[activeSection]?.filter(f => f !== 'category_name').map((field) => (
                <div key={field} className="mb-3">
                  <label className="field-label" htmlFor={`field-${field}`}>
                    {field.replace(/_/g, " ")}
                  </label>
                  <input
                    id={`field-${field}`}
                    type="text"
                    value={formData[field] || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, [field]: e.target.value })
                    }
                    className="field"
                  />
                </div>
              ))}

              {activeSection === "Investment Subcategories" && (
                <div className="mb-3">
                  <label className="field-label" htmlFor="field-category">
                    Category
                  </label>
                  <select
                    id="field-category"
                    value={formData["category_id"] || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        category_id: parseInt(e.target.value),
                      })
                    }
                    className="field"
                  >
                    <option value="">Select Category</option>
                    {investmentCategories.map((cat) => (
                      <option
                        key={cat.id}
                        value={cat.id}
                      >
                        {cat.investment_type}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {activeSection === "Regions" && (
              <div className="mb-3">
                <label className="field-label" htmlFor="field-currency">
                  Currency
                </label>
                <select
                  id="field-currency"
                  value={formData["currency_id"] || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      currency_id: parseInt(e.target.value),
                    })
                  }
                  className="field"
                >
                  <option value="">Select Currency</option>
                  {currencies.map((cur) => (
                    <option
                      key={cur.currency_id}
                      value={cur.currency_id}
                    >
                      {cur.currency_name} ({cur.currency_code})
                    </option>
                  ))}
                </select>
              </div>
            )}

              <div className="mt-5 flex justify-end gap-2 border-t border-[var(--color-rule)] pt-4">
                <button
                  onClick={() => {
                    setShowForm(false);
                    setFormData({});
                    setEditingRow(null);
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  className="btn btn-primary"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
      )}
    </div>
  );
}
