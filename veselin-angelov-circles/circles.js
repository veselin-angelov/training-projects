const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});


function circlesIntersect(circle1, circle2) {
    let distSq = ((circle1.x - circle2.x) * (circle1.x - circle2.x)) + ((circle1.y - circle2.y) * (circle1.y - circle2.y));
    let radSumSq = (circle1.r + circle2.r) * (circle1.r + circle2.r);
    if (distSq === radSumSq) {
        return 0;
    }
    else if (distSq > radSumSq) {
        return -1;
    }
    else {
        return 1;
    }
}

function circlesContain(circle1, circle2) {
    let distSq = parseInt(Math.sqrt(((circle1.x - circle2.x) * (circle1.x - circle2.x)) + ((circle1.y - circle2.y) * (circle1.y - circle2.y))));

    if (distSq + circle2.r === circle1.r) {
        return 1;
    }
    else if (distSq + circle2.r < circle1.r) {
        return 1;
    }
    else {
        return 0;
    }
}

function findCommonElement(array1, array2) {

    // Loop for array1
    for(let i = 0; i < array1.length; i++) {

        // Loop for array2
        for(let j = 0; j < array2.length; j++) {

            // Compare the element of each and
            // every element from both of the
            // arrays
            if(array1[i] === array2[j]) {

                // Return if common element found
                return true;
            }
        }
    }

    // Return if no common element exist
    return false;
}


function question(theQuestion) {
    return new Promise(resolve => readline.question(theQuestion, answer => resolve(parseInt(answer))));
}

async function getInput() {
    const circles = [];

    let n = await question("n >");

    if (n < 2 || n > 1000) {
        readline.close();
        return;
    }

    for (let i = 0; i < n; i++) {
        let x = await question(`x ${i} >`);
        let y = await question(`y ${i} >`);
        let r = await question(`r ${i} >`);

        if (x < -10000 || x > 10000 || y < -10000 || y > 10000 || r < -10000 || r > 10000) {
            readline.close();
            return;
        }

        circles.push({x, y, r});
    }
    readline.close();

    return circles;
}

async function main() {
    // const circles = await getInput();
    // const connections = {};
    //
    // if (circles === undefined) {
    //     return;
    // }
    //
    // for (let i = 0; i < circles.length; i++) {
    //     connections[i] = [];
    // }
    //
    // for (let i = 0; i < circles.length; i++) {
    //     for (let j = 0; j < circles.length; j++) {
    //         if (i === j) {
    //             continue;
    //         }
    //         if (circlesIntersect(circles[i], circles[j]) &&
    //             !circlesContain(circles[i], circles[j]) &&
    //             !circlesContain(circles[j], circles[i])) {
    //             connections[i].push(j);
    //         }
    //     }
    // }
    //
    // let ribs = 1;

    // console.log(Object.keys(connections).length);

    // if (connections[0].includes(circles.length - 1)) {
    //     console.log('1');
    // }

    // let visited = [];
    //
    // for (let i = 0; i < Object.keys(connections).length; i++) {
    //     console.log(connections[i]);
    //     let temp = [];
    //     for (const connection of connections[i]) {
    //         // console.log(connection);
    //         if (!visited.includes(connection)) {
    //             temp.push(connection);
    //         }
    //         if (visited.includes(circles.length - 1)) {
    //             console.log(i);
    //             break;
    //         }
    //     }
    //     // console.log(temp);
    //     visited.push(i);
    //
    // }

    let connections1 = {
        0: [1, 2, 3],
        1: [0, 6, 7],
        2: [0, 4, 5],
        3: [0, 4],
        4: [2, 3, 5, 8],
        5: [2, 4],
        6: [1],
        7: [1, 8]
    }

    let visited = [];
    let index = 0;
    while (index < 8) {
        if (connections1[index].includes(index)) {

        }
        for (const con of connections1[index]) {
            console.log(con);
        }
        console.log('\n');
        index++;
    }

    // console.log(connections);


    // if (circlesIntersect(circles[0].x, circles[0].y, circles[0].r,
    //                      circles[circles.length - 1].x, circles[circles.length - 1].y, circles[circles.length - 1].r)) {
    //     console.log('1');
    // }
    // else {
    //     console.log('algorithm');
    // }

}

main();

// circles.push([0, 0, 1]);
// circles.push([4, 0, 4]);
// circles.push([1, 0, 2]);

// let x1 = 0, y1 = 0, r1 = 1;
// let x2 = 4, y2 = 0, r2 = 4;
// let x3 = 1, y3 = 0, r3 = 2;

// let t = circlesIntersect(x1, y1, r1, x2, y2, r2);
// console.log(t);
//
// t = circlesIntersect(x1, y1, r1, x2, y2, r2);
// console.log(t);