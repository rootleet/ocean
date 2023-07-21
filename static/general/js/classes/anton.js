class Anton {

    // calculate xyz
    lineXyz(line){
        let x = $(`#x_${line}`).val()
        let y = $(`#y_${line}`).val()
        let z = parseFloat(x*y).toFixed(2)
        console.log(x)
        $(`#z_${line}`).val(z)
    }

}

class LineCalculate {
    #calculate(line, operator) {
        const x = Number($(`#x_${line}`).val());
        const y = Number($(`#y_${line}`).val());
        let z;

        switch(operator) {
            case 'sub': z = x - y; break;
            case 'mul': z = x * y; break;
            case 'div': z = x / y; break;
            case 'add': z = x + y; break;
            default:
                console.error(`Invalid operator: ${operator}`);
                return;
        }

        $(`#z_${line}`).val(z.toFixed(2));
    }

    add(line) {
        this.#calculate(line, 'add');
    }

    sub(line) {
        this.#calculate(line, 'sub');
    }

    mul(line) {
        this.#calculate(line, 'mul');
    }

    div(line) {
        this.#calculate(line, 'div');
    }
}

const anton = new Anton();
const lincal = new LineCalculate()