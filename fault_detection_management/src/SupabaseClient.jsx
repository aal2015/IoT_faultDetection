import { createClient } from '@supabase/supabase-js'

const supabaseUrl = "https://itjkuwyfonbaesfgnxen.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0amt1d3lmb25iYWVzZmdueGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzNjA4OTEsImV4cCI6MjA1OTkzNjg5MX0.0y6KgPoe74N5QGVJKV-MhEvO7W71txcJfaPDkIdtGKc"

export const supabase = createClient(supabaseUrl, supabaseAnonKey)