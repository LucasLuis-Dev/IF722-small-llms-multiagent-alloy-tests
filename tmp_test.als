
signature Requirement {}
signature TestCase {
    covers: set Requirement
}

pred someTestCaseIsWritten {
    some tc: TestCase | some tc.covers
}

// Positive Instances (expect 1)

run {
    someTestCaseIsWritten
    #TestCase = 1
    #Requirement = 1
    one tc: TestCase, one r: Requirement | tc.covers = r
} for 4 expect 1

run {
    someTestCaseIsWritten
    #TestCase = 1
    #Requirement = 2
    one tc: TestCase | #tc.covers = 2
} for 4 expect 1

run {
    someTestCaseIsWritten
    #TestCase = 2
    #Requirement = 1
    let tc1, tc2: TestCase, r1: Requirement | {
        tc1.covers = r1
        tc2.covers = none
    }
} for 4 expect 1

run {
    someTestCaseIsWritten
    #TestCase = 2
    #Requirement = 2
    all tc: TestCase | some tc.covers
} for 4 expect 1

run {
    someTestCaseIsWritten
    #TestCase = 3
    #Requirement = 3
    let tc1, tc2, tc3: TestCase, r1, r2, r3: Requirement | {
        tc1.covers = r1
        tc2.covers = r2 + r3
        tc3.covers = none
    }
} for 4 expect 1

// Negative Instances (expect 0)

run {
    not someTestCaseIsWritten
    #TestCase = 1
    #Requirement = 1
    one tc: TestCase | no tc.covers
} for 4 expect 0

run {
    not someTestCaseIsWritten
    #TestCase = 2
    #Requirement = 1
    all tc: TestCase | no tc.covers
} for 4 expect 0

run {
    not someTestCaseIsWritten
    #TestCase = 2
    no Requirement
    all tc: TestCase | no tc.covers
} for 4 expect 0

run {
    not someTestCaseIsWritten
    #TestCase = 1
    #Requirement = 2
    one tc: TestCase | no tc.covers
} for 4 expect 0

run {
    not someTestCaseIsWritten
    #TestCase = 3
    #Requirement = 3
    all tc: TestCase | no tc.covers
} for 4 expect 0