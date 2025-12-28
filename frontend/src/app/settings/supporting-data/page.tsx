'use client';

import React, { useEffect, useState } from "react";

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
      const res = await fetch("/api/categories/investment-category");
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
    const res = await fetch("/api/categories/currencies");
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
      const res = await fetch(`/api${sections[section]}`);
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
      const res = await fetch(`/api${sections[section]}/${id}`, {
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
    <div className="mb-4 shadow-lg">
      <h1 className="text-2xl font-bold mb-4">Master Data Configuration</h1>

      <div className="flex justify-between items-center p-3 bg-[var(--color-card)] rounded-t-2xl transition-all duration-200">
        {Object.keys(sections).map((s) => (
          <button
            key={s}
            onClick={() => setActiveSection(s)}
            className={`px-10 py-1 rounded-xl ${
              activeSection === s
                ? "bg-[var(--color-accent)] text-black"
                : "bg-[var(--color-bg-lighter)] text-white"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <div className="flex justify-between p-2 bg-[var(--color-card)]">
          <h2 className="text-2xl font-semibold text-[var(--color-accent)]">
            {activeSection}
          </h2>
          <button
            onClick={() => {
              setShowForm(true);
              setEditingRow(null);
              setFormData({});
            }}
            className="bg-[var(--color-accent)] hover:opacity-90 text-black px-6 py-1 rounded-xl"
          >
            + Add
          </button>
        </div>

        {data[activeSection]?.length > 0 ? (
          <table className="min-w-full border border-gray-700 text-sm bg-[var(--color-bg-lighter)]">
            <thead>
              <tr className="text-left border-b border-gray-500">
                {fieldMappings[activeSection]?.map((field) => (
                  <th key={field} className="p-2 capitalize">
                    {field.replace(/_/g, " ")}
                  </th>
                ))}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data[activeSection].map((row, idx) => {
                const idKey = idKeyMappings[activeSection];
                const rowId = row[idKey];
                return (
                  <tr key={rowId || idx} className="border-b border-gray-700 ">
                    {fieldMappings[activeSection]?.map((field) => (
                      <td key={field} className="p-2">
                        {row[field] || '-'}
                      </td>
                    ))}
                    <td className="p-2 space-x-2">
                      <button
                        onClick={() => handleEdit(row)}
                        className="bg-blue-400 px-3 py-1 rounded text-white"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(activeSection, rowId)}
                        className="bg-red-400 px-3 py-1 rounded text-white"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p>No records found.</p>
        )}

        {showForm && (
          <div className="fixed inset-0 flex items-center justify-center ">
            <div className="bg-gray-900 p-6 rounded-2xl shadow-2xl w-[400px]">
              <h3 className="text-lg font-semibold mb-4">
                {editingRow ? `Edit ${activeSection}` : `Add New ${activeSection}`}
              </h3>

              {fieldMappings[activeSection]?.filter(f => f !== 'category_name').map((field) => (
                <div key={field} className="mb-3">
                  <label className="block text-sm capitalize mb-1 text-gray-300">
                    {field.replace(/_/g, " ")}
                  </label>
                  <input
                    type="text"
                    value={formData[field] || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, [field]: e.target.value })
                    }
                    className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
                  />
                </div>
              ))}

              {activeSection === "Investment Subcategories" && (
                <div className="mb-3">
                  <label className="block text-sm capitalize mb-1 text-gray-300">
                    Category
                  </label>
                  <select
                    value={formData["category_id"] || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        category_id: parseInt(e.target.value),
                      })
                    }
                    className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
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
                <label className="block text-sm capitalize mb-1 text-gray-300">
                  Currency
                </label>
                <select
                  value={formData["currency_id"] || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      currency_id: parseInt(e.target.value),
                    })
                  }
                  className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
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

              <div className="flex justify-end gap-2 mt-4">
                <button
                  onClick={() => {
                    setShowForm(false);
                    setFormData({});
                    setEditingRow(null);
                  }}
                  className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-white"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  className="bg-[var(--color-accent)] hover:opacity-90 px-4 py-2 rounded text-black"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}