function rollD6Dice() {
    const d6Faces = ["🎲", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"];
    let roll = Math.floor(Math.random() * 6) + 1;
    document.getElementById("dice-display").innerHTML = d6Faces[roll];
    document.getElementById("dice-number").innerHTML = roll;
}
function rollD20Dice()
{

    const d20Faces = [
        "/static/images/d20_20Start.png","/static/images/d20_1.png", "/static/images/d20_2.png", "/static/images/d20_3.png", "/static/images/d20_4.png", "/static/images/d20_5.png", "/static/images/d20_6.png",
        "/static/images/d20_7.png", "/static/images/d20_8.png", "/static/images/d20_9.png", "/static/images/d20_10.png", "/static/images/d20_11.png", "/static/images/d20_12.png",
        "/static/images/d20_13.png", "/static/images/d20_14.png", "/static/images/d20_15.png", "/static/images/d20_16.png", "/static/images/d20_17.png", "/static/images/d20_18.png",
        "/static/images/d20_19.png", "/static/images/d20_20.png"
    ];
    let roll = Math.floor(Math.random() * 20) + 1;
    let imagePath = `/static/images/d20_${roll}.png`;
    document.getElementById("d20-display").src = imagePath;
    document.getElementById("d20-number").innerHTML = roll;
}