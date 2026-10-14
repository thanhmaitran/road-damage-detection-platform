import { NavLink } from "react-router-dom";

const links = [["/", "Home"], ["/detect", "Detection"], ["/analytics", "Analytics"], ["/model", "Model Insights"]];

export default function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main">
      <h1>Road Damage Detection</h1>
      {links.map(([to, label]) => (
        <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "active" : "")}>{label}</NavLink>
      ))}
    </nav>
  );
}
