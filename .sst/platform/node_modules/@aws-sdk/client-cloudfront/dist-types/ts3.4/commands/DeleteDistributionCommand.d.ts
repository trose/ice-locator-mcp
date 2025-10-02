import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { DeleteDistributionRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteDistributionCommandInput
  extends DeleteDistributionRequest {}
export interface DeleteDistributionCommandOutput extends __MetadataBearer {}
export declare class DeleteDistributionCommand extends $Command<
  DeleteDistributionCommandInput,
  DeleteDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DeleteDistributionCommandInput, DeleteDistributionCommandOutput>;
  private serialize;
  private deserialize;
}
