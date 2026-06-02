sig User {
  follows: set User,
  posts: set Photo,
  suggested: set User
}
sig Influencer extends User {}
sig Photo {}
sig Ad extends Photo {}

run TestPositive2 {
  one u: User | u.follows = u and u.follows = none
} for 4 expect 0
