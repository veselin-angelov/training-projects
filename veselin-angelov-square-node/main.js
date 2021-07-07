const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});


function square(a) {
    let allDiag = new Set();
    for (let x = 1; x <= a; x++) {
        for (let y = x + 1; y <= a; y++) {
            let hypot = Math.sqrt(x*x + y*y);
            if (hypot % 1 === 0) {
                allDiag.add(hypot);
            }
        }
    }

    if (allDiag.size === 0) {
        return {
            longest: 0,
            count: 0,
        }
    }

    return {
        longest: Math.max(...Array.from(allDiag)),
        count: allDiag.size,
    }
}

readline.question('>', answer => {
    let result = square(answer);
    console.log(result.longest, result.count);
    readline.close();
})
