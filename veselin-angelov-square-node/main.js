const fs = require('fs')
const { createCanvas } = require('canvas')
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});


function square(a, context) {
    let allDiag = new Set();
    for (let x = 1; x <= a; x++) {
        for (let y = x + 1; y <= a; y++) {
            let hypot = Math.sqrt(x*x + y*y);
            if (hypot % 1 === 0) {
                allDiag.add(hypot);
                context.strokeStyle = '#952020';
                context.moveTo(100, 100);
                context.lineTo((x * 100) + 100, (y * 100) + 100);
                context.stroke();
                context.beginPath();
                context.arc((x * 100) + 100,(y * 100) + 100,10,0,Math.PI*2, false);
                context.fill();
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
    const width = (answer * 100) + 200;
    const height = (answer * 100) + 200;


    const canvas = createCanvas(width, height);
    const context = canvas.getContext('2d');

    context.fillStyle = '#aaa';
    context.fillRect(0, 0, width, height);
    context.fillStyle = '#fff';
    context.fillRect(100, 100, width - 200, height - 200);
    context.fillStyle = '#000';

    context.font = 'bold 20pt Menlo';
    context.fillText(answer.toString(), width / 2, 50);
    context.font = '10pt Menlo';

    for (let x = 0; x <= answer * 100; x++) {
        if (x % 100 === 0) {
            context.fillText((x/100).toString(), x + 100, 100);
        }
    }

    for (let y = 0; y <= answer * 100; y++) {
        if (y % 100 === 0) {
            context.fillText((y/100).toString(), 90, y + 100);
        }
    }

    let result = square(answer, context);

    context.font = 'bold 20pt Menlo';
    context.fillText('Longest: ' + result.longest.toString(), width / 4, height - 50);
    context.fillText('Count: ' + result.count.toString(), width / 2, height - 50);

    console.log(result.longest, result.count);

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync('./test.png', buffer);

    readline.close();
})
