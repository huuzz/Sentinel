"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useAuth } from "@/features/auth/auth-provider";
import { authenticatedGet } from "@/lib/api";

type ManagedUser = {id:string;email:string;role:string;is_active:boolean};
export default function UsersPage() {
  const { token, user } = useAuth(); const [users,setUsers]=useState<ManagedUser[]>([]); const [message,setMessage]=useState("");
  const load=useCallback(()=>{if(token)return authenticatedGet<ManagedUser[]>("/api/v1/users",token).then(setUsers);},[token]);
  useEffect(()=>{void load();},[load]);
  async function create(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!token)return;const form=event.currentTarget;const data=new FormData(form);const response=await fetch("/api/backend/users",{method:"POST",headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json"},body:JSON.stringify({email:data.get("email"),password:data.get("password"),role:data.get("role")})});setMessage(response.ok?"User created":"Could not create user");if(response.ok){form.reset();void load();}}
  if(user?.role!=="ADMIN")return <p className="empty">Administrator access required.</p>;
  return <><header className="page-header"><div><p className="eyebrow">Administration</p><h1>User access</h1><p>Create role-scoped SentinelAI accounts.</p></div></header><section className="login-card"><form onSubmit={create}><label>Email<input name="email" type="email" required/></label><label>Temporary password<input name="password" type="password" minLength={12} required/></label><label>Role<select name="role"><option>VIEWER</option><option>ANALYST</option><option>ADMIN</option></select></label><button className="button">Create user</button>{message&&<p>{message}</p>}</form></section><section className="panel table-wrap"><table><thead><tr><th>Email</th><th>Role</th><th>Active</th></tr></thead><tbody>{users.map(item=><tr key={item.id}><td>{item.email}</td><td>{item.role}</td><td>{item.is_active?"Yes":"No"}</td></tr>)}</tbody></table></section></>;
}
