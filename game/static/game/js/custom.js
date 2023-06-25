let draggedElement;

// Function to check if all empty cells are filled
function checkEmptyCells() {
  const emptyCells = document.querySelectorAll('.empty-cell');
  const remainingEmptyCells = Array.from(emptyCells).filter(cell => !cell.querySelector('.letter'));
  const guessButton = document.getElementById('guessButton');

  // Enable or disable the Guess button based on remaining empty cells
  if (guessButton && remainingEmptyCells.length === 0) {
    guessButton.disabled = false;
  } else {
    guessButton.disabled = true;
  }
}


function allowDrop(event) {
  event.preventDefault();
}

function handleDragStart(event) {
  event.dataTransfer.setData("id", event.target.id);
  event.target.classList.add('dragging');
  draggedElement = event.target;
  const lettersList = document.getElementById('letters');
  lettersList.classList.add('letters-list');
  checkEmptyCells();
}

function handleDragEnd(event) {
  event.target.classList.remove('dragging');
  const lettersList = document.getElementById('letters');
  lettersList.classList.remove('letters-list');
  checkEmptyCells();
}

function handleDrop(event) {
  event.preventDefault();

  const letterId = event.dataTransfer.getData("id");
  const letterElement = document.querySelector(`[id="${letterId}"]`);
  const emptyCell = event.target.closest('.empty-cell');
  const existingLetter = emptyCell.querySelector('.letter');

  const lettersList = document.getElementById('letters');

  if (existingLetter) {
    const returnedLetter = document.createElement("div");
    returnedLetter.classList.add("letter", "letter-cell");
    returnedLetter.innerText = existingLetter.innerText;
    returnedLetter.draggable = true;
    returnedLetter.id = existingLetter.id;
    returnedLetter.addEventListener('dragstart', handleDragStart);
    returnedLetter.addEventListener('dragend', handleDragEnd);
    lettersList.appendChild(returnedLetter);
  }

  letterElement.remove();

  const newLetterElement = document.createElement("div");
  newLetterElement.classList.add("letter");
  newLetterElement.innerText = letterElement.innerText;
  newLetterElement.draggable = true;
  newLetterElement.id = letterId;
  newLetterElement.addEventListener('dragstart', handleDragStart);
  newLetterElement.addEventListener('dragend', handleDragEnd);

  emptyCell.innerHTML = '';
  emptyCell.appendChild(newLetterElement);
  checkEmptyCells();
}

function returnLetter(emptyCell) {
  const letterElement = emptyCell.querySelector('.letter');
  if (letterElement) {
    const letterId = letterElement.id;
    const lettersList = document.getElementById('letters');
    const letterToRestore = document.querySelector(`[id="${letterId}"]`);

    if (letterToRestore) {
      const newLetterElement = document.createElement("div");
      newLetterElement.classList.add("letter", "letter-cell");
      newLetterElement.innerText = letterElement.innerText;
      newLetterElement.draggable = true;
      newLetterElement.id = letterToRestore.id;
      newLetterElement.addEventListener('dragstart', handleDragStart);
      newLetterElement.addEventListener('dragend', handleDragEnd);
      lettersList.appendChild(newLetterElement);
    }

    emptyCell.removeChild(letterElement);
  }
  checkEmptyCells();
}

function fillEmptyCell(letter) {
  const emptyCells = document.querySelectorAll('.empty-cell');
  for (let i = 0; i < emptyCells.length; i++) {
    const emptyCell = emptyCells[i];
    if (emptyCell.innerHTML === '') {
      const newLetterElement = document.createElement("div");
      newLetterElement.classList.add("letter");
      newLetterElement.innerText = letter.innerText;
      newLetterElement.draggable = true;
      newLetterElement.id = letter.id;
      newLetterElement.addEventListener('dragstart', handleDragStart);
      newLetterElement.addEventListener('dragend', handleDragEnd);

      emptyCell.appendChild(newLetterElement);
      letter.remove();
      break;
    }
  }
  checkEmptyCells();
}

document.addEventListener('DOMContentLoaded', function() {

  // Add event listeners to letter elements
  const letters = document.querySelectorAll('.letter-cell');
  letters.forEach(letter => {
    letter.addEventListener('dragstart', handleDragStart);
    letter.addEventListener('dragend', handleDragEnd);
  });

  // Add event listener to the form to prevent submission
  const guessForm = document.getElementById('guess-form');

  if (guessForm) {
        guessForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Process the guessed answer
        const emptyCells = document.querySelectorAll('.empty-cell');
        const wordsLengths = words_lengths;
          console.log(words_lengths)
        let guessedAnswer = '';
        let letterIndex = 0;
        let wordIndex = 0;

        emptyCells.forEach((cell) => {
          letterIndex++;
          const letter = cell.querySelector('.letter');
          if (letter) {
            guessedAnswer += letter.innerText;
            if (wordsLengths[wordIndex] == letterIndex) {
              guessedAnswer += ' ';
              letterIndex = 0;
              wordIndex++;
            }
          }
        });

        // Assign the guessed answer to the hidden input field
        const answerInput = document.querySelector('input[name="answer"]');
        answerInput.value = guessedAnswer.trim();

        // Submit the form
        guessForm.submit();
      });

      // Clone the source set of letters for drag and drop
      const sourceSet = document.getElementById('letters');
      const sourceLetters = sourceSet.innerHTML;
      const dropContainers = document.querySelectorAll('.word-container');

      // Add event listener to the drop containers to handle drag and drop
      dropContainers.forEach(container => {
        container.addEventListener('dragover', function(event) {
          event.preventDefault();
        });
        container.addEventListener('drop', function(event) {
          handleDrop(event);
        });
      });

      // Reset the source set of letters on form reset
      guessForm.addEventListener('reset', function() {
        sourceSet.innerHTML = sourceLetters;
      });

      // Add click event listener to the letters list
      const letterList = document.getElementById('letters');
      letterList.addEventListener('click', function(event) {
        const letter = event.target;
        if (letter.classList.contains('letter-cell')) {
          fillEmptyCell(letter);
        }
      });
  };
});