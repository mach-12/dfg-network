/* eslint no-use-before-define: 0 */  // --> OFF

import React, { useState } from 'react';
import data from './data/data.json';
import { ForceGraph2D } from 'react-force-graph';
import Modal from 'react-modal';
import './App.css';


Modal.setAppElement('#root');

const App = () => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [nodeData, setNodeData] = useState({});

  const handleNodeClick = (node) => {
    setNodeData(node);
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setNodeData({});
  };

  return (
    <div className="App">
      <header className="App-header">
        Develop For Good: Network
        <a href="https://github.com/mach-12/dfg-network" target="_blank" rel="noopener noreferrer" className="github-link">
          <i className="fab fa-github"></i> Check out the GitHub Repository!
        </a>
      </header>

      <section className="Main">
        <ForceGraph2D
          graphData={data}
          onNodeClick={handleNodeClick}
          nodeAutoColorBy="group"
          backgroundColor="light"
        />
      </section>

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Node Details"
        className="modal"
        overlayClassName="overlay"
      >
        <h2>Node Details</h2>
        {nodeData.image && <img src={nodeData.image} alt={nodeData.name} style={{ width: '100px', height: '100px' }} />}
        {nodeData.linkedin_url && <p><a href={nodeData.linkedin_url} target="_blank" rel="noopener noreferrer">LinkedIn Profile</a></p>}
        <p><strong>ID:</strong> {nodeData.id}</p>
        <p><strong>Name:</strong> {nodeData.name}</p>
        <p><strong>Description:</strong> {nodeData.profile}</p>
        <button onClick={closeModal}>Close</button>
      </Modal>
    </div>
  );
};

export default App;
