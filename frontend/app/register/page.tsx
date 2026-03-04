"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Role = "customer" | "reviewer" | "seller";

export default function RegisterPage(){

  const router = useRouter()

  const [fullName,setFullName] = useState("")
  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")
  const [role,setRole] = useState<Role>("customer")

  const [showPw,setShowPw] = useState(false)
  const [error,setError] = useState("")
  const [loading,setLoading] = useState(false)

  async function handleRegister(e:React.FormEvent){

    e.preventDefault()

    setError("")

    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    try{

      setLoading(true)

      const res = await fetch(`${apiUrl}/users/signup`,{

        method:"POST",

        headers:{
          "Content-Type":"application/json"
        },

        body: JSON.stringify({

          full_name: fullName,
          email,
          password,
          role

        })

      })

      const data = await res.json().catch(()=>({}))

      if(!res.ok){
        setError(data?.detail || "Unable to create account.")
        return
      }

      router.push("/login")

    }catch{

      setError("Unable to connect to server.")

    }finally{

      setLoading(false)

    }

  }

  return(

    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">

      <div className="w-full max-w-md">

        <div className="mb-6">

          <h1 className="text-3xl font-bold text-gray-900">
            WhatToDo NYC
          </h1>

          <p className="mt-2 text-gray-700">
            Join the community discovering authentic places in New York City.
          </p>

        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">

          <h2 className="text-xl font-semibold text-gray-900">
            Create account
          </h2>

          {error && (

            <div className="mt-4 border border-red-300 bg-red-50 rounded-xl px-4 py-3">

              <p className="text-sm text-red-800">
                {error}
              </p>

            </div>

          )}

          <form onSubmit={handleRegister} className="mt-5 space-y-4">

            <div>

              <label className="block text-sm font-semibold text-gray-900">
                Full name
              </label>

              <input
                placeholder="Your name"
                className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:ring-4 focus:ring-black/10 focus:border-gray-400 outline-none"
                value={fullName}
                onChange={(e)=>setFullName(e.target.value)}
                required
              />

            </div>

            <div>

              <label className="block text-sm font-semibold text-gray-900">
                Email
              </label>

              <input
                type="email"
                placeholder="you@example.com"
                className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:ring-4 focus:ring-black/10 focus:border-gray-400 outline-none"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                required
              />

            </div>

            <div>

              <label className="block text-sm font-semibold text-gray-900">
                Account type
              </label>

              <select
                className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:ring-4 focus:ring-black/10 focus:border-gray-400 outline-none"
                value={role}
                onChange={(e)=>setRole(e.target.value as Role)}
              >

                <option value="customer">Explorer</option>
                <option value="reviewer">Reviewer</option>
                <option value="seller">Business Owner</option>

              </select>

            </div>

            <div>

              <label className="block text-sm font-semibold text-gray-900">
                Password
              </label>

              <div className="mt-2 relative">

                <input
                  type={showPw ? "text" : "password"}
                  placeholder="Create a password"
                  className="w-full border border-gray-300 rounded-xl px-4 py-3 pr-16 text-gray-900 focus:ring-4 focus:ring-black/10 focus:border-gray-400 outline-none"
                  value={password}
                  onChange={(e)=>setPassword(e.target.value)}
                  required
                />

                <button
                  type="button"
                  onClick={()=>setShowPw(!showPw)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold px-3 py-1 border rounded-lg hover:bg-gray-50"
                >
                  {showPw ? "Hide" : "Show"}
                </button>

              </div>

            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-black text-white py-3 rounded-xl font-semibold hover:bg-gray-900 disabled:opacity-70"
            >
              {loading ? "Creating account..." : "Create account"}
            </button>

          </form>

          <p className="mt-5 text-sm text-gray-800">
            Already have an account?{" "}
            <a href="/login" className="font-semibold text-black hover:underline">
              Sign in
            </a>
          </p>

        </div>

      </div>

    </div>

  )

}