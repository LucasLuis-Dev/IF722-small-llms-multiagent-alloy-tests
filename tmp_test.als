```alloy
sig User {
  password: one Password // Every User has exactly one Password
}

sig Password {}
// Constraint: Every Password belongs to exactly one User.
// This means the inverse of the 'password' relation (p.~password) must be
// a function from Password to User, where each Password is mapped to exactly one User.
fact {
  all p: Password | one (p.~password)
// Generate an instance where the number of Users and Passwords is at most 4.
// Due to the bijections defined by the 'password' field and the fact,
// the number of User instances will always be equal to the number of Password instances.
run {} for 4
```