const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

const fs = require("fs");
const { createCanvas } = require('canvas');


function question(theQuestion) {
    return new Promise(resolve => readline.question(theQuestion, answer => resolve(parseInt(answer))));
}


async function getInput() {
    let k = await question("K >"); // Y
    let l = await question("L >"); // X
    let r = await question("R >");

    if (k < 0 || k > 1000 || l < 0 || l > 1000 || k > l || r < 0 || r > 100) {
        readline.close();
        return;
    }

    let strawberries = new Array(k).fill(1).map(() => new Array(l).fill(1));

    for (let i = 0; i < 2; i++) {
        let y = await question(`S${i} Y >`);
        let x = await question(`S${i} X >`);
        strawberries[k - y][x - 1] = 0;

        if (i === 0) {
            let stop = await question(`Stop (1/0) >`);
            if (stop) {
                break;
            }
        }
    }
    readline.close();

    return {
        k,
        l,
        r,
        strawberries
    }
}


async function main() {
    const input = await getInput();

    const canvas = createCanvas(input.l * 100 + 100, input.k * 100 + 100);
    const context = canvas.getContext('2d');

    context.fillStyle = '#aaa';
    context.strokeStyle = '#000';
    context.fillRect(0, 0, input.l * 100 + 100, input.k * 100 + 100);

    for (let y = 0; y < input.k; y++) {
        for (let x = 0; x < input.l; x++) {
            if (input.strawberries[y][x] === 0) {
                context.fillStyle = '#1a186a';
                context.beginPath();
                context.arc(100 * (x + 1),100 * (y + 1),10,0,Math.PI*2, false);
                context.fill();
                context.closePath();
            }
        }
    }

    for (let i = 0; i < input.r; i++) {
        let tempStrawberries = input.strawberries.map(e => [...e]);
        for (let y = 0; y < input.k; y++) {
            for (let x = 0; x < input.l; x++) {
                if (input.strawberries[y][x] === 0) {
                    if (y - 1 >= 0) {
                        tempStrawberries[y - 1][x] = 0;
                    }
                    if (y + 1 < input.k) {
                        tempStrawberries[y + 1][x] = 0;
                    }
                    if (x - 1 >= 0) {
                        tempStrawberries[y][x - 1] = 0;
                    }
                    if (x + 1 < input.l) {
                        tempStrawberries[y][x + 1] = 0;
                    }
                }
            }
        }
        input.strawberries = tempStrawberries.map(e => [...e]);
    }

    console.log(input.strawberries);

    let count = 0;
    input.strawberries.forEach((row) => {
        row.forEach((number) => {
            if (number === 1) {
                count++;
            }
        });
    });

    console.log(count);

    for (let y = 0; y < input.k; y++) {
        for (let x = 0; x < input.l; x++) {
            if (input.strawberries[y][x] === 0) {
                context.fillStyle = '#ff0000';
                context.beginPath();
                context.arc(100 * (x + 1),100 * (y + 1),5,0,Math.PI*2, false);
                context.fill();
                context.closePath();
            }
            else {
                context.fillStyle = '#00ff04';
                context.beginPath();
                context.arc(100 * (x + 1),100 * (y + 1),5,0,Math.PI*2, false);
                context.fill();
                context.closePath();
            }
        }
    }


    context.fillStyle = '#791717';
    context.font = '10pt Menlo';
    context.fillText(`Height: ${input.k}, Width: ${input.l}, Days: ${input.r}, Good strawberries: ${count}`, 90, 50);

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync('./test.png', buffer);
}

main();
