'use client';

import { useEffect, useRef, useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

type User = { user_id: number; name: string };
type IncomeSource = { income_source_id: number; name: string; description?: string };
type ExpenseCategory = { expense_category_id: number; name: string; description?: string };
type InvestmentCategory = { id: number; investment_type: string };
type InvestmentSubcategory = { id: number; investment_subcategory_name: string; category_id: number };
type Currency = { currency_id: number; currency_name: string; currency_code: string };
type Region = { region_id: number; region_name: string; currency_id: number };
type Unit = { unit_id: number; unit_name: string };

export default function TransactionsPage() {
  const [activeTab, setActiveTab] = useState<'income' | 'expense' | 'investment'>('income');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [incomeSources, setIncomeSources] = useState<any[]>([]);
  const [expenseCategories, setExpenseCategories] = useState([]);
  const [investmentCategories, setInvestmentCategories] = useState([]);
  const [investmentSubcats, setInvestmentSubcats] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [regions, setRegions] = useState([]);
  const [units, setUnits] = useState([]);
  const [recent, setRecent] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const formRef = useRef<HTMLDivElement | null>(null);

  // form data for each tab
  const [incomeForm, setIncomeForm] = useState<any>({});
  const [expenseForm, setExpenseForm] = useState<any>({});
  const [investmentForm, setInvestmentForm] = useState<any>({});
  
  // Import Modal State
  const [showImportModal, setShowImportModal] = useState(false);
  const [importForm, setImportForm] = useState({
      user_id: "",
      bank_name: "",
      file: null as File | null,
      currency: "INR" 
  });
  const [availableBanks, setAvailableBanks] = useState<string[]>([]);

  // Map endpoints for investment types -> endpoint
  const investmentEndpointMap: Record<number, string> = {
    1: "http://localhost:8000/investment/bullion",       // Bullion
    9: "http://localhost:8000/investment/crypto",        // Crypto
    2: "http://localhost:8000/investment/stocks",        // Indian Stock
    3: "http://localhost:8000/investment/real-estate",   // Land
    5: "http://localhost:8000/investment/mutual-fund",   // Mutual Fund
  };

  // load reference data once
  useEffect(() => {
    async function loadRefs() {
      try {
        const [
          usersRes,
          incRes,
          expRes,
          invCatRes,
          invSubRes,
          curRes,
          regRes,
          unitRes
        ] = await Promise.all([
          fetch("http://localhost:8000/categories/users").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/income-sources").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/expense-category").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/investment-category").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/investment-subcategory").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/currencies").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/region").then(r => r.json()).catch(() => []),
          fetch("http://localhost:8000/categories/units").then(r => r.json()).catch(() => [])
        ]);

        setUsers(usersRes || []);
        setIncomeSources(incRes || []);
        setExpenseCategories(expRes || []);
        setInvestmentCategories(invCatRes || []);
        setInvestmentSubcats(invSubRes || []);
        setCurrencies(curRes || []);
        setRegions(regRes || []);
        setUnits(unitRes || []);
      } catch (err) {
        console.error("Failed to load reference data", err);
      }
    }
    loadRefs();
  }, []);


// Fetch active tab to do calculations
useEffect(() => {
  setCurrentPage(1);
  fetchRecent();
}, [activeTab]);

async function fetchRecent() {
  try {
    let records: any[] = [];

    if (activeTab === "expense") {
      const res = await fetch("http://localhost:8000/expenses");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    } else if (activeTab === "investment") {
      const endpoints = Object.values(investmentEndpointMap);
      const responses = await Promise.allSettled(
        endpoints.map((endpoint) => fetch(endpoint))
      );

      const allData = await Promise.all(
        responses
          .filter((r): r is PromiseFulfilledResult<Response> => r.status === "fulfilled")
          .map((r) => r.value.json())
      );

      records = allData.flatMap((d) => (Array.isArray(d) ? d : d?.results || []));
    } else {
      // default = income
      const res = await fetch("http://localhost:8000/income");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    }

    // Sort all tabs by their relevant date field
    const sorted = records.sort((a: any, b: any) => {
      const dateA = new Date(a.earned_date || a.spent_date || a.investment_date || a.date || 0);
      const dateB = new Date(b.earned_date || b.spent_date || b.investment_date || b.date || 0);
      return dateB.getTime() - dateA.getTime(); // latest first
    });
    setRecent(sorted);
  } catch (err) {
    console.error("fetchRecent error", err);
    setRecent([]);
  }
}

  // helper to map id -> display name using loaded refs
  function userName(id?: number) {
    if (!id) return "";
    const u = users.find(x => x.user_id === Number(id));
    return u?.name ?? String(id);
  }
  function incomeSourceName(id?: number) {
    if (!id) return "";
    const s = incomeSources.find(x => x.income_source_id === Number(id));
    return s?.name ?? String(id);
  }
  function expenseCategoryName(id?: number) {
    if (!id) return "";
    const s = expenseCategories.find(x => x.expense_category_id === Number(id));
    return s?.name ?? String(id);
  }
  function investmentTypeName(id?: number) {
    if (!id) return "";
    const s = investmentCategories.find(x => x.id === Number(id));

    return s?.investment_type ?? String(id);
  }
  function invSubName(id?: number) {
    if (!id) return "";
    const s = investmentSubcats.find(x => x.id === Number(id));
    return s?.investment_subcategory_name ?? String(id);
  }



  function currencyCode(id?: number) {
    if (!id) return "";
    const s = currencies.find(x => x.currency_id === Number(id));
    return s?.currency_code ?? String(id);
  }

  // Submit handlers
  async function submitIncome(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const body = {
        user_id: Number(incomeForm.user_id),
        source_id: Number(incomeForm.income_source_id || incomeForm.source_id || incomeForm.source),
        amount: Number(incomeForm.amount),
        currency: incomeForm.currency || (currencies[0]?.currency_code ?? "INR"),
        earned_date: new Date(incomeForm.earned_date).toISOString()
      };
      const res = await fetch("http://localhost:8000/income", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`Income POST failed: ${res.status} ${JSON.stringify(body)}`);
      alert("Income saved");
      //setIncomeForm({});
      await fetchRecent();
    } catch (err) {
      console.error(err);
      alert("Failed to save income (see console)");
    } finally {
      setLoading(false);
    }
  }

  async function submitExpense(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const body = {
        user_id: Number(expenseForm.user_id),
        category_id: Number(expenseForm.category_id),
        amount: Number(expenseForm.amount),
        currency: expenseForm.currency || (currencies[0]?.currency_code ?? "INR"),
        spent_date: new Date(expenseForm.spent_date).toISOString()
      };
      const res = await fetch("http://localhost:8000/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`Expense POST failed: ${res.status} ${JSON.stringify(body)}`);
      alert("Expense saved");
//       setExpenseForm({});
      await fetchRecent();
    } catch (err) {
      console.error(err);
      alert("Failed to save expense (see console)");
    } finally {
      setLoading(false);
    }
  }

  // Investment submission - choose endpoint based on investment_type_id
  async function submitInvestment(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);

    try {
      const invType = Number(investmentForm.investment_type_id || investmentForm.investment_type);
      const endpoint = investmentEndpointMap[invType] ?? "http://localhost:8000/investment/stocks";

      // Build payload according to your sample structures.
      // We'll try to fill minimal required fields depending on type.
      let payload: any = {
        investor: Number(investmentForm.investor),
        currency_id: Number(investmentForm.currency_id),
        investment_type_id: invType,
        investment_subcategory_id: investmentForm.investment_subcategory_id ? Number(investmentForm.investment_subcategory_id) : null,
        investment_date: investmentForm.investment_date || new Date().toISOString().substring(0, 10),
        transaction_type: investmentForm.transaction_type || "BUY"
      };

      // additional fields based on type
      if (invType === 2) {
        // Indian Stock
        payload = {
          ...payload,
          stock_symbol: investmentForm.stock_symbol || "UNKNOWN",
          stock_name: investmentForm.stock_name || investmentForm.stock_symbol || "Stock",
          initial_price_per_stock: Number(investmentForm.initial_price_per_stock || investmentForm.price || 0),
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          stock_quantity: Number(investmentForm.stock_quantity || 0)
        };
      } else if (invType === 5) {
        // Mutual Fund
        payload = {
          ...payload,
          scheme_code: investmentForm.scheme_code || investmentForm.scheme || "",
          fund_name: investmentForm.fund_name || investmentForm.scheme_name || "",
          initial_price_per_unit: investmentForm.initial_price_per_unit || investmentForm.initial_price || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          unit_quantity: Number(investmentForm.unit_quantity || 0),
          total_amount_after_sale: Number(investmentForm.total_amount_after_sale || 0)
        };
      } else if (invType === 1) {
        // Bullion
        payload = {
          ...payload,
          metal_name: investmentForm.metal_name || invSubName(investmentForm.investment_subcategory_id) || "Gold",
          initial_price_per_gram: investmentForm.initial_price_per_gram || investmentForm.initial_price || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          quantity_in_grams: Number(investmentForm.quantity_in_grams || 0)
        };
      } else if (invType === 3) {
        // Land / Real estate
        payload = {
          ...payload,
          property_name: investmentForm.property_name || "Property",
          property_location: investmentForm.property_location || "",
          property_type: investmentForm.property_type || "Plot",
          initial_price_per_sqyds: investmentForm.initial_price_per_sqyds || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          area_in_sqyds: Number(investmentForm.area_in_sqyds || 0)
        };
      } else if (invType === 9) {
        // Crypto
        payload = {
          ...payload,
          coin_symbol: investmentForm.coin_symbol || investmentForm.stock_symbol || "BTC",
          crypto_name: investmentForm.crypto_name || investmentForm.coin_symbol || "Crypto",
          initial_price_per_coin: Number(investmentForm.initial_price_per_coin || 0),
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          coin_quantity: Number(investmentForm.coin_quantity || 0),
          total_amount_after_sale: Number(investmentForm.total_amount_after_sale || 0)
        };
      }

      // POST
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Investment POST failed: ${res.status} ${txt}`);
      }
      alert("Investment saved");
//       setInvestmentForm({});
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to save investment: " + (err?.message || ""));
    } finally {
      setLoading(false);
    }
  }

  // Filtered subcategories when investment type changes
  const filteredInvestmentSubcats = (typeId?: number) =>
    investmentSubcats.filter(s => s.category_id === Number(typeId));

  function formatDate(dateStr: string) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

function formatAmount(amount: any, currency?: string) {
  if (!amount) return "0";

  const num = Number(amount);
  const symbolMap: Record<string, string> = {
    INR: "₹",
    USD: "$",
    EUR: "€",
    PLN: "zł",
    GBP: "£",
    JPY: "¥"
  };

  // Normalize currency to uppercase in case API sends lowercase
  const symbol = symbolMap[currency?.toUpperCase?.()] || '';

  // Format number using locale
  const formatted = num.toLocaleString('en-IN', { maximumFractionDigits: 2 });

  return `${symbol}${formatted}`;
}

  // Pagination
  const totalPages = Math.ceil(recent.length / itemsPerPage);
  const paginatedData = recent.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Quick scroll-to-form using floating + button
  function scrollToForm() {
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // small helper to render recent rows replacing ids with names where possible
  function renderRecentCell(key: string, value: any) {
    if (key.toLowerCase().includes("user") || key === "user_id") return userName(value);
    if (key.toLowerCase().includes("source") || key === "source_id" || key === "income_source_id") return incomeSourceName(value);
    if (key.toLowerCase().includes("category") && activeTab === "expense") return expenseCategoryName(value);
    if (key.toLowerCase().includes("investment_type") || key === "investment_type_id") return investmentTypeName(value);
    if (key.toLowerCase().includes("investment_subcategory") || key === "investment_subcategory_id") return invSubName(value);
    if (key.toLowerCase().includes("currency")) return currencyCode(value);
    // else default
    return (value === null || value === undefined) ? "" : String(value);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br p-6 space-y-4">
      <div className="max-w-8xl mx-auto space-y-2">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold">Transactions</h1>
            <p className="text-1xl font-semibold">Track your income, expenses, and investments</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                  setShowImportModal(true);
                  fetch("http://localhost:8000/import/banks")
                      .then(r => r.json())
                      .then(data => setAvailableBanks(data))
                      .catch(err => console.error("Failed to fetch banks", err));
              }}
              className="bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-2 px-4 rounded-md text-sm font-semibold transition"
            >
              Import CSV
            </button>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-2 px-4 rounded-md text-sm font-semibold transition"
            >
              {showForm ? '✕ Close' : '+ New Transaction'}
            </button>
          </div>
        </div>


        {/* Tabs - Full Width */}
        <div className="flex rounded-2xl p-1.5 shadow-md mb-8" style={{ backgroundColor: 'var(--color-card)' }}>
          {(['income', 'expense', 'investment'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className="flex-1 px-6 py-2.5 rounded-xl font-medium transition-all"
              style={{
                backgroundColor: activeTab === tab ? 'var(--color-accent)' : 'transparent',
                color: activeTab === tab ? 'var(--color-text-pie)' : 'var(--color-text-primary)',
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Form - Slide down animation */}
        {showForm && (
            <div ref={formRef} className="rounded-2xl p-6 shadow-xl animate-slideDown mb-8" style={{ backgroundColor: 'var(--color-card)' }}>
              <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--color-text-secondary)' }}>
                Add {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
              </h2>

              {/* Income Form */}
              {activeTab === "income" && (
                  <form onSubmit={submitIncome} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select user dropdown */}
                      <div>
                        <select value={incomeForm.user_id ?? ""} onChange={(e) => setIncomeForm({...incomeForm, user_id: e.target.value})} className={selectClass}>
                            <option value="">Select User</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={incomeForm.currency ?? ""} onChange={(e) => setIncomeForm({...incomeForm, currency: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select income source dropdown */}
                      <div>
                        <select value={incomeForm.income_source_id ?? ""} onChange={(e) => setIncomeForm({...incomeForm, income_source_id: e.target.value})} className={selectClass}>
                            <option value="">Select Income Source</option>
                                {incomeSources.map(s => <option key={s.income_source_id} value={s.income_source_id}>{s.name}</option>)}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" value={incomeForm.amount ?? ""} onChange={(e) => setIncomeForm({...incomeForm, amount: e.target.value})} placeholder="Amount" className={inputClass} />
                      </div>

                      {/* Date calendar */}
                      <div className="flex flex-col">
                        <DatePicker className="react-datepicker"
                          selected={incomeForm.earned_date ? new Date(incomeForm.earned_date) : null}
                          onChange={(date) =>
                            setIncomeForm({
                              ...incomeForm,
                              earned_date: date ? date.toISOString().split("T")[0] : "",
                            })
                          }
                          dateFormat="yyyy-MM-dd"
                          className={`${inputClass} w-full`}
                          placeholderText="Select date"
                          showPopperArrow={false}
                          calendarClassName="rounded-2xl shadow-lg border border-gray-200"
                        />
                      </div>

                      {/* Checkboxes for recurring entries and auto learn */}
                      <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2">
                          <input type="checkbox" checked={!!incomeForm.is_recurring} onChange={(e) => setIncomeForm({...incomeForm, is_recurring: e.target.checked})} />
                          <span className="text-sm">Recurring</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="checkbox" checked={!!incomeForm.auto_learn} onChange={(e) => setIncomeForm({...incomeForm, auto_learn: e.target.checked})} />
                          <span className="text-sm">Auto-learn</span>
                        </label>
                      </div>

                    </div>

                    {/* save income button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="px-6 py-2.5 rounded-xl font-medium disabled:opacity-50" style={{ backgroundColor: 'var(--color-accent)', color: 'var(--color-text-pie)' }}>
                      {loading ? "Saving..." : "Save Income"}
                      </button>
                    </div>

                  </form>
              )}

              {/* Expense Form */}
              {activeTab === "expense" && (
                  <form onSubmit={submitExpense} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select user dropdown */}
                      <div>
                        <select value={expenseForm.user_id ?? ""} onChange={(e) => setExpenseForm({...expenseForm, user_id: e.target.value})}   className={selectClass}>
                            <option value="">Select User</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={expenseForm.currency ?? ""} onChange={(e) => setExpenseForm({...expenseForm, currency: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select expense category dropdown */}
                      <div>
                        <select value={expenseForm.category_id ?? ""} onChange={(e) => setExpenseForm({...expenseForm, category_id: e.target.value})} className={selectClass}>
                            <option value="">Select Category</option>
                            {expenseCategories.map(c => <option key={c.expense_category_id} value={c.expense_category_id}>{c.name}</option>)}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" value={expenseForm.amount ?? ""} onChange={(e) => setExpenseForm({...expenseForm, amount: e.target.value})} placeholder="Amount" className={inputClass} />
                      </div>


                      {/* Date calendar */}
                      <div>
                          <input type="date"
                            value={incomeForm.earned_date ?? ""}
                            onChange={(e) =>
                              setIncomeForm({ ...incomeForm, earned_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer text-[var(--color-text-primary)]`}
                            style={{
                              backgroundColor: 'var(--color-bg)',
                              borderColor: 'var(--color-bg-lighter)',
                              color: 'var(--color-text-primary)',
                              colorScheme: 'dark',
                              padding: '0.6rem 0.8rem',
                              borderRadius: '0.75rem',
                            }}
                          />
                      </div>

                      {/* Checkboxes for recurring entries and auto learn */}
                      <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2">
                          <input type="checkbox" checked={!!expenseForm.is_recurring} onChange={(e) => setExpenseForm({...expenseForm, is_recurring: e.target.checked})} />
                          <span className="text-sm">Recurring</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="checkbox" checked={!!expenseForm.auto_learn} onChange={(e) => setExpenseForm({...expenseForm, auto_learn: e.target.checked})} />
                          <span className="text-sm">Auto-learn</span>
                        </label>
                      </div>

                    </div>

                    {/* save expense button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="px-6 py-2.5 rounded-xl font-medium disabled:opacity-50" style={{ backgroundColor: 'var(--color-accent)', color: 'var(--color-text-pie)' }}>
                      {loading ? "Saving..." : "Save Expense"}
                      </button>
                    </div>

                  </form>
              )}

              {/* Investment Form */}
              {activeTab === "investment" && (
                  <form onSubmit={submitInvestment} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select investor dropdown */}
                      <div>
                        <select value={investmentForm.investor ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investor: e.target.value})} className={selectClass}>
                          <option value="">Select Investor</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={investmentForm.currency_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, currency_id: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_id}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select investment category dropdown */}
                      <div>
                        <select value={investmentForm.investment_type_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investment_type_id: Number(e.target.value), investment_subcategory_id: undefined})} className={selectClass}>
                            <option value="">Investment Type</option>
                            {investmentCategories.map(ic => <option key={ic.id} value={ic.id}>{ic.investment_type}</option>)}
                        </select>
                      </div>

                      {/* Dependent subcategory dropdown: show only when there are sub categories */}
                      <div>
                        <select value={investmentForm.investment_subcategory_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investment_subcategory_id: e.target.value})} className={selectClass}>
                            <option value="">Subcategory (if applicable)</option>
                                {filteredInvestmentSubcats(investmentForm.investment_type_id).map(s => (
                            <option key={s.id} value={s.id}>{s.investment_subcategory_name}</option>
                            ))}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" placeholder="Total invested amount" value={investmentForm.total_invested_amount ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, total_invested_amount: e.target.value})} className={inputClass} />
                      </div>

                      {/* Date calendar */}
                      <div>
                          <input type="date"
                            value={incomeForm.earned_date ?? ""}
                            onChange={(e) =>
                              setIncomeForm({ ...incomeForm, earned_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer text-[var(--color-text-primary)]`}
                            style={{
                              backgroundColor: 'var(--color-bg)',
                              borderColor: 'var(--color-bg-lighter)',
                              color: 'var(--color-text-primary)',
                              colorScheme: 'dark',
                              padding: '0.6rem 0.8rem',
                              borderRadius: '0.75rem',
                            }}
                          />
                      </div>

                      {/* Based on investment type, show type-specific fields */}
                      {/* Type-specific helper fields (stock example) */}
                      {Number(investmentForm.investment_type_id) === 2 && (
                          <>
                           <input placeholder="Stock symbol" value={investmentForm.stock_symbol ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_symbol: e.target.value})} className={inputClass} />
                           <input placeholder="Stock name" value={investmentForm.stock_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_name: e.target.value})} className={inputClass} />
                           <input type="number" step="0.01" placeholder="Price per stock" value={investmentForm.initial_price_per_stock ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_stock: e.target.value})} className={inputClass} />
                           <input type="number" step="0.0001" placeholder="Quantity" value={investmentForm.stock_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_quantity: e.target.value})} className={inputClass} />
                          </>
                      )}

                      {/* Mutual Fund fields */}
                      {Number(investmentForm.investment_type_id) === 5 && (
                          <>
                            <input placeholder="Scheme code" value={investmentForm.scheme_code ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, scheme_code: e.target.value})} className={inputClass} />
                            <input placeholder="Fund name" value={investmentForm.fund_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, fund_name: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Unit quantity" value={investmentForm.unit_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, unit_quantity: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Price per unit" value={investmentForm.initial_price_per_unit ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_unit: e.target.value})} className={inputClass} />
                          </>
                      )}

                      {/* Bullion fields */}
                      {Number(investmentForm.investment_type_id) === 1 && (
                          <>
                            <input placeholder="Metal name (Gold/Silver)" value={investmentForm.metal_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, metal_name: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Price per gram" value={investmentForm.initial_price_per_gram ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_gram: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Quantity (grams)" value={investmentForm.quantity_in_grams ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, quantity_in_grams: e.target.value})} className={inputClass} />
                          </>
                      )}

                      {/* Crypto fields */}
                      {Number(investmentForm.investment_type_id) === 9 && (
                        <>
                          <input placeholder="Coin symbol" value={investmentForm.coin_symbol ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, coin_symbol: e.target.value})} className={inputClass} />
                          <input placeholder="Crypto name" value={investmentForm.crypto_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, crypto_name: e.target.value})} className={inputClass} />
                          <input type="number" placeholder="Quantity" value={investmentForm.coin_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, coin_quantity: e.target.value})} className={inputClass} />
                        </>
                      )}

                    </div>

                    {/* save investment button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="px-6 py-2.5 rounded-xl font-medium disabled:opacity-50" style={{ backgroundColor: 'var(--color-accent)', color: 'var(--color-text-pie)' }}>
                      {loading ? "Saving..." : "Save Investment"}
                      </button>
                    </div>

                  </form>
              )}
            </div>
        )}

            {/* Recent Transactions - Card Style */}
            <div className="rounded-2xl shadow-xl overflow-hidden" style={{ backgroundColor: 'var(--color-card)' }}>
              <div className="p-4 border-b" style={{ borderColor: 'var(--color-bg-lighter)' }}>
                <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-secondary)' }}>Recent {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}s</h3>
              </div>

              <div className="divide-y" style={{ borderColor: 'var(--color-bg-lighter)' }}>
                {console.log("This is the pagination data: ", {paginatedData})}
                {paginatedData.map((item: any, idx) => (
                  <div key={idx} className="p-6 transition-colors hover:opacity-90" style={{ backgroundColor: idx % 2 === 0 ? 'var(--color-card)' : 'var(--color-bg-lighter)' }}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{
                            backgroundColor: activeTab === 'income' ? '#10b98150' :
                                           activeTab === 'expense' ? '#ef444450' : '#3b82f650'
                          }}>
                            <span className="text-lg">
                              {activeTab === 'income' ? '↓' : activeTab === 'expense' ? '↑' : '💰'}
                            </span>
                          </div>
                          <div>
                              <p className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                                {activeTab === 'income'
                                  ? incomeSourceName(item.source_id)
                                  : activeTab === 'expense'
                                    ? expenseCategoryName(item.category_id)
                                    : `${investmentTypeName(item.investment_type_id)} : ${invSubName(item.investment_subcategory_id) || (item.stock_symbol || item.fund_name || item.metal_name || 'Investment')}`
                                }
                              </p>
                              <p className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                                {userName(item.user_id || item.investor)} • {formatDate(item.earned_date || item.spent_date || item.investment_date)}
                              </p>
                          </div>
                        </div>
                      </div>

                      {/* Amount column */}
                      <div className="text-right">
                        <p className="text-lg font-semibold" style={{
                          color: activeTab === 'income' ? '#10b981' :
                                 activeTab === 'expense' ? '#ef4444' : '#3b82f6'
                        }}>
                           {formatAmount(
                            activeTab === 'investment'
                              ? item.total_invested_amount || 0
                              : activeTab === 'income'
                              ? item.amount || 0
                              : item.amount,
                              item.currency_id ? currencyCode(item.currency_id) : item.currency || ''
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="p-4 flex items-center justify-between border-t" style={{ borderColor: 'var(--color-bg-lighter)' }}>
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="px-4 py-2 rounded-lg disabled:opacity-50 transition-all"
                    style={{ backgroundColor: 'var(--color-bg-lighter)', color: 'var(--color-text-primary)' }}
                  >
                    Previous
                  </button>
                  <span style={{ color: 'var(--color-text-primary)' }}>
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 rounded-lg disabled:opacity-50 transition-all"
                    style={{ backgroundColor: 'var(--color-bg-lighter)', color: 'var(--color-text-primary)' }}
                  >
                    Next
                  </button>
                </div>
              )}
            </div>

            <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>

      </div>

      {/* Floating + button scrolls to form */}
      <button onClick={scrollToForm} className="fixed bottom-8 right-8 bg-[var(--color-accent)] text-black p-4 rounded-full shadow-lg hover:bg-[var(--color-accent-hover)]">
        +
      </button>

      {/* Import Modal */}
      {showImportModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[var(--color-card)] p-8 rounded-2xl w-full max-w-lg shadow-2xl relative">
                  <button 
                      onClick={() => setShowImportModal(false)}
                      className="absolute top-4 right-4 text-gray-400 hover:text-white"
                  >
                      ✕
                  </button>
                  <h2 className="text-2xl font-bold mb-6 text-[var(--color-text-primary)]">Import Transactions</h2>
                  
                  <div className="space-y-4">
                      {/* User Select */}
                      <div>
                          <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">User</label>
                          <select 
                              value={importForm.user_id} 
                              onChange={(e) => setImportForm({...importForm, user_id: e.target.value})}
                              className={selectClass}
                          >
                              <option value="">Select User</option>
                              {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                          </select>
                      </div>

                      {/* Bank Select */}
                      <div>
                          <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Bank</label>
                          <select 
                              value={importForm.bank_name} 
                              onChange={(e) => setImportForm({...importForm, bank_name: e.target.value})}
                              className={selectClass}
                          >
                              <option value="">Select Bank</option>
                              {availableBanks.map(bank => (
                                  <option key={bank} value={bank}>{bank.toUpperCase()}</option>
                              ))}
                          </select>
                      </div>

                       {/* Currency Select */}
                       <div>
                          <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Currency</label>
                          <select 
                              value={importForm.currency} 
                              onChange={(e) => setImportForm({...importForm, currency: e.target.value})}
                              className={selectClass}
                          >
                              {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                          </select>
                      </div>

                      {/* File Upload */}
                       <div>
                          <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">CSV File</label>
                          <input 
                              type="file" 
                              accept=".csv"
                              onChange={(e) => setImportForm({...importForm, file: e.target.files?.[0] || null})}
                              className={`${inputClass} !p-2`}
                          />
                      </div>

                      {/* Submit */}
                      <div className="pt-4 flex justify-end">
                          <button 
                              onClick={async () => {
                                  if (!importForm.user_id || !importForm.bank_name || !importForm.file) {
                                      alert("Please fill all fields");
                                      return;
                                  }
                                  
                                  const formData = new FormData();
                                  formData.append("user_id", importForm.user_id);
                                  formData.append("bank_name", importForm.bank_name);
                                  formData.append("currency", importForm.currency);
                                  formData.append("file", importForm.file);

                                  try {
                                      const res = await fetch("http://localhost:8000/import/transactions", {
                                          method: "POST",
                                          body: formData
                                      });
                                      const data = await res.json();
                                      if(!res.ok) throw new Error(data.detail || "Import failed");
                                      
                                      alert(`Imported ${data.processed} transactions successfully!`);
                                      setShowImportModal(false);
                                      fetchRecent(); // refresh list
                                  } catch (err: any) {
                                      alert("Error: " + err.message);
                                  }
                              }}
                              className="w-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-3 rounded-xl font-bold transition"
                          >
                              Upload & Import
                          </button>
                      </div>
                  </div>
              </div>
          </div>
      )}
    </div>
  );
}

const inputClass = 'w-full px-4 py-2.5 rounded-xl border border-[var(--color-bg-lighter)] bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)/30] transition-all';
const selectClass = 'w-full px-4 py-2.5 rounded-xl border border-[var(--color-bg-lighter)] bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)/30] transition-all';