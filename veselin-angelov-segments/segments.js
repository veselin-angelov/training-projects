const fs = require("fs");
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

const { createCanvas } = require('canvas');


function question(theQuestion) {
    return new Promise(resolve => readline.question(theQuestion, answer => resolve(parseInt(answer))));
}


async function getInput() {
    let n = await question("len >");
    let a = await question("a >");
    let b = await question("b >");
    let c = await question("c >");

    if (n < 0 || n > 100000 || a < 0 || a > 100000 || b < 0 || b > 100000 || c < 0 || c > 100000) {
        readline.close();
        return;
    }

    readline.close();

    return {
        n,
        a,
        b,
        c
    }
}

async function main() {
    const input = await getInput();

    const canvas = createCanvas(input.n * 100 + 200, 200);
    const context = canvas.getContext('2d');

    context.fillStyle = '#aaa';
    context.fillRect(0, 0, input.n * 100 + 200, 200);

    context.strokeStyle = '#000';
    context.moveTo(100, 100);
    context.lineTo(100 * (input.n + 1), 100);
    context.stroke();
    context.fillStyle = '#000';

    for (let i = 0; i <= input.n; i++) {
        context.beginPath();
        context.arc(100 * (i + 1),100,5,0,Math.PI*2, false);
        context.fill();
        context.closePath();
    }

    const segmentsSet = new Set();

    let len = 0;
    for (let i = 0; i <= input.n / input.a; i++) {
        segmentsSet.add(len);
        len += input.a;
    }

    len = input.n - input.b;
    for (let i = 0; i < Math.floor(input.n / input.b); i++) {
        segmentsSet.add(len);
        len -= input.b;
    }

    const segments = Array.from(segmentsSet).sort(function(a, b) {return a - b;});

    let colored = 0;

    context.beginPath();
    context.strokeStyle = '#ff0000';
    for (let i = 0; i < input.n; i++) {
        if (segments.includes(i) && segments.includes(i + 1)) {
            colored++;
            context.moveTo(100 * (i + 1), 100);
            context.lineTo(100 * (i + 1) + 100, 100);
        }
    }
    context.stroke();
    console.log(input.n - colored);

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync('./test.png', buffer);
}

main();
