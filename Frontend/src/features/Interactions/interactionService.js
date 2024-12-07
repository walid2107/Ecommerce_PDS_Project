import axios from "axios";
import { base_url, config } from "../../utils/axiosConfig";

const createInteraction = async (data) => {
    const response = await axios.post(`${base_url}interaction/`, data, config);
    if (response.data) {
      return response.data;
    }
  };


  export const interactionSevice = {createInteraction}